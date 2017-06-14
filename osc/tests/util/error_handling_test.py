from django.conf import settings
from django.test import TestCase
from mock import Mock

from osc.util.error_handling import SlackErrorHandler


class SlackErrorHandlerTest(TestCase):

    def test_create_handler_dont_post_message_to_slack(self):

        error_handler = SlackErrorHandler(
            settings.SLACK['token'],
            0,
            settings.WEB['url'])

        mock_slacker = Mock()
        error_handler.slack = mock_slacker

        mock_slacker.chat.post_message.assert_not_called()

    def test_dont_post_message_to_slack_when_flush_if_no_error(self):

        error_handler = SlackErrorHandler(
            settings.SLACK['token'],
            0,
            settings.WEB['url'])

        mock_slacker = Mock()
        error_handler.slack = mock_slacker

        error_handler.flush()

        mock_slacker.chat.post_message.assert_not_called()

    def test_post_message_to_slack_when_handles_error(self):

        error_handler = SlackErrorHandler(
            settings.SLACK['token'],
            0,
            settings.WEB['url'])

        mock_slacker = Mock()
        error_handler.slack = mock_slacker

        error_handler.error(
            process_name='TEST',
            module_name=__name__,
            function_name=__package__,
            message='Error test message',
            actionable_info={'info': 'text'})

        mock_slacker.chat.post_message.assert_called_once()

    def test_post_message_to_slack_when_handles_warning(self):

        error_handler = SlackErrorHandler(
            settings.SLACK['token'],
            0,
            settings.WEB['url'])

        mock_slacker = Mock()
        error_handler.slack = mock_slacker

        error_handler.warning(
            process_name='TEST',
            module_name=__name__,
            function_name=__package__,
            message='Warning test message',
            actionable_info={'info': 'text'})

        mock_slacker.chat.post_message.assert_called_once()

    def test_post_message_to_slack_when_handles_info(self):

        error_handler = SlackErrorHandler(
            settings.SLACK['token'],
            0,
            settings.WEB['url'])

        mock_slacker = Mock()
        error_handler.slack = mock_slacker

        error_handler.info(
            process_name='TEST',
            module_name=__name__,
            function_name=__package__,
            message='Info test message',
            actionable_info={'info': 'text'})

        mock_slacker.chat.post_message.assert_called_once()

    def test_dont_flush_if_message_count_less_than_bucket_size(self):

        bucket_size = 3
        error_handler = SlackErrorHandler(
            settings.SLACK['token'],
            bucket_size,
            settings.WEB['url']
        )

        mock_slacker = Mock()
        error_handler.slack = mock_slacker

        error_handler.info(
            process_name='TEST',
            module_name=__name__,
            function_name=__package__,
            message='Info test message',
            actionable_info={'info': 'text'})

        mock_slacker.chat.post_message.assert_not_called()

        error_handler.error(
            process_name='TEST',
            module_name=__name__,
            function_name=__package__,
            message='Error test message',
            actionable_info={'info': 'text'})

        mock_slacker.chat.post_message.assert_not_called()

        error_handler.warning(
            process_name='TEST',
            module_name=__name__,
            function_name=__package__,
            message='Warning test message',
            actionable_info={'info': 'text'})

        mock_slacker.chat.post_message.assert_called_once()

    def test_flush_once_per_bucket_size(self):
        bucket_size = 10

        error_handler = SlackErrorHandler(
            settings.SLACK['token'],
            bucket_size,
            settings.WEB['url']
        )

        mock_slacker = Mock()
        error_handler.slack = mock_slacker

        i = 0
        while i < 30:
            i += 1
            error_handler.info(
                process_name='TEST',
                module_name=__name__,
                function_name=__package__,
                message='Info test message',
                actionable_info={'info': 'text'})

        assert (mock_slacker.chat.post_message.call_count == 30 / bucket_size)
