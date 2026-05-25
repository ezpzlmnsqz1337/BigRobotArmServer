from __future__ import annotations

import threading
import time
import uuid
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable

JobExecutor = Callable[[str], str]
JobPayload = dict[str, Any]
JobEventCallback = Callable[[JobPayload], None]


class JobConflictError(RuntimeError):
    pass


class JobQueueFullError(RuntimeError):
    pass


@dataclass
class JobRecord:
    job_id: str
    name: str
    commands: list[str]
    total: int
    current_index: int = 0
    status: str = 'queued'
    last_response: str | None = None
    error: str | None = None
    cancel_requested: bool = False
    created_at: float = field(default_factory=time.time)
    started_at: float | None = None
    finished_at: float | None = None

    def to_payload(self) -> JobPayload:
        return {
            'jobId': self.job_id,
            'name': self.name,
            'status': self.status,
            'currentIndex': self.current_index,
            'total': self.total,
            'lastResponse': self.last_response,
            'error': self.error,
            'cancelRequested': self.cancel_requested,
            'createdAt': self.created_at,
            'startedAt': self.started_at,
            'finishedAt': self.finished_at,
        }


class JobManager:
    def __init__(
        self,
        executor: JobExecutor,
        event_callback: JobEventCallback,
        max_queued_jobs: int = 3,
    ):
        self._executor = executor
        self._event_callback = event_callback
        self._lock = threading.RLock()
        self._jobs: dict[str, JobRecord] = {}
        self._active_job_id: str | None = None
        self._pending_job_ids: deque[str] = deque()
        self._max_queued_jobs = max_queued_jobs

    def has_active_job(self) -> bool:
        with self._lock:
            if self._active_job_id is None:
                return False

            job = self._jobs.get(self._active_job_id)
            if job is None:
                self._active_job_id = None
                return False

            return job.status in ('queued', 'running')

    def has_pending_jobs(self) -> bool:
        with self._lock:
            return bool(self._pending_job_ids)

    def has_open_job_queue(self) -> bool:
        with self._lock:
            return self.has_active_job() or self.has_pending_jobs()

    def submit_job(self, commands: list[str], name: str | None = None) -> JobPayload:
        normalized_commands = self._normalize_commands(commands)

        with self._lock:
            if len(self._pending_job_ids) >= self._max_queued_jobs:
                raise JobQueueFullError('Job queue is full')

            job = JobRecord(
                job_id=self._create_job_id(),
                name=name or 'Untitled job',
                commands=normalized_commands,
                total=len(normalized_commands),
            )
            self._jobs[job.job_id] = job
            if self._active_job_id is None:
                self._active_job_id = job.job_id
                should_start = True
            else:
                self._pending_job_ids.append(job.job_id)
                should_start = False

        self._emit('jobQueued', job)

        if should_start:
            self._start_job_worker(job.job_id)
        return job.to_payload()

    def get_job_status(self, job_id: str | None = None) -> JobPayload | None:
        with self._lock:
            if job_id is None:
                job_id = self._active_job_id

            if job_id is None:
                return None

            job = self._jobs.get(job_id)
            if job is None:
                return None

            return job.to_payload()

    def cancel_job(self, job_id: str) -> JobPayload | None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return None

            if job.status not in ('queued', 'running'):
                return job.to_payload()

            job.cancel_requested = True

            if job.job_id in self._pending_job_ids:
                self._pending_job_ids.remove(job.job_id)
                job.status = 'cancelled'
                job.finished_at = time.time()
                self._emit('jobCancelled', job)

            return job.to_payload()

    def get_queue_snapshot(self) -> list[JobPayload]:
        with self._lock:
            queued_ids = []
            if self._active_job_id is not None:
                queued_ids.append(self._active_job_id)
            queued_ids.extend(self._pending_job_ids)
            return [
                self._jobs[job_id].to_payload()
                for job_id in queued_ids
                if job_id in self._jobs
            ]

    def _start_job_worker(self, job_id: str) -> None:
        worker = threading.Thread(target=self._run_job, args=(job_id,), daemon=True)
        worker.start()

    def _run_job(self, job_id: str) -> None:
        with self._lock:
            job = self._jobs[job_id]
            job.status = 'running'
            job.started_at = time.time()

        self._emit('jobStarted', job)

        while True:
            with self._lock:
                job = self._jobs[job_id]

                if job.cancel_requested:
                    job.status = 'cancelled'
                    job.finished_at = time.time()
                    self._finish_current_job_locked()
                    self._emit('jobCancelled', job)
                    return

                if job.current_index >= job.total:
                    job.status = 'completed'
                    job.finished_at = time.time()
                    self._finish_current_job_locked()
                    self._emit('jobCompleted', job)
                    return

                command = job.commands[job.current_index]

            try:
                response = self._executor(command)
            except Exception as error:
                with self._lock:
                    job = self._jobs[job_id]
                    job.status = 'failed'
                    job.error = str(error)
                    job.finished_at = time.time()
                    self._finish_current_job_locked()
                    self._emit('jobFailed', job)
                return

            with self._lock:
                job = self._jobs[job_id]
                job.last_response = response
                job.current_index += 1

            self._emit('jobProgress', job)

    def _normalize_commands(self, commands: list[str]) -> list[str]:
        if not isinstance(commands, list) or not commands:
            raise ValueError(
                'Job commands must be a non-empty array of command strings'
            )

        normalized_commands: list[str] = []
        for command in commands:
            if not isinstance(command, str):
                raise ValueError('Job commands must be strings')

            normalized = command.strip()
            if not normalized:
                raise ValueError('Job commands cannot contain empty strings')

            normalized_commands.append(normalized)

        return normalized_commands

    def _create_job_id(self) -> str:
        return f'job-{uuid.uuid4().hex[:10]}'

    def _finish_current_job_locked(self) -> None:
        self._active_job_id = None
        if self._pending_job_ids:
            next_job_id = self._pending_job_ids.popleft()
            self._active_job_id = next_job_id
            self._start_job_worker(next_job_id)

    def _emit(self, event_type: str, job: JobRecord) -> None:
        self._event_callback({'type': event_type, 'job': job.to_payload()})