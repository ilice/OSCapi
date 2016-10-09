from django.test import TestCase
from django.utils import timezone
from osc.models import BatchProcess
from osc.services.batch_process_service import *
from datetime import timedelta


class BatchProcessServiceTest(TestCase):
    def setUp(self):
        self.first_time = timezone.now() - timedelta(days=100)
        BatchProcess.objects.create(name='IR_D',
                                    status='S',
                                    date_launched=self.first_time)
        self.second_time = self.first_time + timedelta(days=10)
        BatchProcess.objects.create(name='IR_D',
                                    status='S',
                                    date_launched=self.second_time)
        self.third_time = self.first_time
        BatchProcess.objects.create(name='IR_H',
                                    status='S',
                                    date_launched=self.third_time)

        self.fourth_time = self.second_time + timedelta(days=10)
        BatchProcess.objects.create(name='IR_H',
                                    status='S',
                                    date_launched=self.fourth_time)

    def test_new_batchprocess_get_inserted(self):
        """ Inserting a new batchprocess works"""
        start_batch_process('IR_D', timezone.now())

        self.assertEqual(BatchProcess.objects.count(), 5)
        self.assertEqual(BatchProcess.objects.filter(name='IR_D').count(), 3)
        self.assertEqual(BatchProcess.objects.filter(name='IR_D', status='S').count(), 2)
        self.assertEqual(BatchProcess.objects.filter(name='IR_D', status='P').count(), 1)

        start_batch_process('IR_H', timezone.now())

        self.assertEqual(BatchProcess.objects.count(), 6)
        self.assertEqual(BatchProcess.objects.filter(name='IR_H').count(), 3)
        self.assertEqual(BatchProcess.objects.filter(name='IR_H', status='S').count(), 2)
        self.assertEqual(BatchProcess.objects.filter(name='IR_H', status='P').count(), 1)

    def test_latest_time_is_correct(self):
        """ Inserting a new batchprocess works"""
        date = timezone.now()

        p_id = start_batch_process('IR_D', date)

        lastdate = get_latest_date_launched('IR_D')

        self.assertEqual(lastdate, self.second_time)

    def test_success_batch_process(self):
        date = timezone.now()

        p_id = start_batch_process('IR_D', date)

        lastdate = get_latest_date_launched('IR_D')

        self.assertEqual(lastdate, self.second_time)

        success_batch_process(p_id)

        lastdate = get_latest_date_launched('IR_D')

        self.assertEqual(lastdate, date)

    def test_fail_batch_process(self):
        date = timezone.now()

        p_id = start_batch_process('IR_D', date)

        lastdate = get_latest_date_launched('IR_D')

        self.assertEqual(lastdate, self.second_time)

        fail_batch_process(p_id)

        lastdate = get_latest_date_launched('IR_D')

        self.assertEqual(lastdate, self.second_time)
