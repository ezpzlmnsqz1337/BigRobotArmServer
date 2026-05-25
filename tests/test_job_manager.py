import threading
import time
import unittest

from job_manager import JobManager, JobPayload, JobQueueFullError


class JobManagerTests(unittest.TestCase):
    def test_runs_job_and_emits_progress(self):
        events: list[JobPayload] = []
        commands_run: list[str] = []

        def executor(command: str) -> str:
            commands_run.append(command)
            return f'OK {command}\nBigRobotArm::READY\n'

        manager = JobManager(executor, events.append)
        job = manager.submit_job(['G0 B0 S0 E0 WR0 W0', 'G28'], 'demo')

        self._wait_for_status(manager, job['jobId'], 'completed')

        final_status = manager.get_job_status(job['jobId'])
        self.assertIsNotNone(final_status)
        assert final_status is not None
        self.assertEqual(final_status['status'], 'completed')
        self.assertEqual(final_status['currentIndex'], 2)
        self.assertEqual(commands_run, ['G0 B0 S0 E0 WR0 W0', 'G28'])
        self.assertEqual(
            [event['type'] for event in events],
            ['jobQueued', 'jobStarted', 'jobProgress', 'jobProgress', 'jobCompleted'],
        )

    def test_queues_second_job_until_first_completes(self):
        events: list[JobPayload] = []
        commands_run: list[str] = []
        release_first_job = threading.Event()

        def executor(command: str) -> str:
            commands_run.append(command)
            if command == 'G0 B0 S0 E0 WR0 W0':
                release_first_job.wait(timeout=1)
            return f'OK {command}\nBigRobotArm::READY\n'

        manager = JobManager(executor, events.append)
        first_job = manager.submit_job(['G0 B0 S0 E0 WR0 W0'], 'first')
        second_job = manager.submit_job(['G28'], 'second')

        time.sleep(0.05)
        first_status = manager.get_job_status(first_job['jobId'])
        second_status = manager.get_job_status(second_job['jobId'])
        assert first_status is not None
        assert second_status is not None
        self.assertEqual(first_status['status'], 'running')
        self.assertEqual(second_status['status'], 'queued')

        release_first_job.set()

        self._wait_for_status(manager, first_job['jobId'], 'completed')
        self._wait_for_status(manager, second_job['jobId'], 'completed')
        self.assertEqual(commands_run, ['G0 B0 S0 E0 WR0 W0', 'G28'])

    def test_rejects_when_pending_queue_is_full(self):
        events: list[JobPayload] = []
        release_jobs = threading.Event()

        def executor(command: str) -> str:
            release_jobs.wait(timeout=1)
            return f'OK {command}\nBigRobotArm::READY\n'

        manager = JobManager(executor, events.append, max_queued_jobs=1)
        manager.submit_job(['G0 B0 S0 E0 WR0 W0'], 'first')
        manager.submit_job(['G28'], 'second')

        with self.assertRaises(JobQueueFullError):
            manager.submit_job(['M503'], 'third')

        release_jobs.set()

    def _wait_for_status(self, manager: JobManager, job_id: str, expected_status: str):
        for _ in range(100):
            status = manager.get_job_status(job_id)
            if status is not None and status['status'] == expected_status:
                return
            time.sleep(0.02)
        self.fail(f'Job {job_id} did not reach status {expected_status}')


if __name__ == '__main__':
    unittest.main()