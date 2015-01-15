#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from tempest.api.monitoring import base
from tempest.common.utils import data_utils
from tempest import exceptions
from tempest import test


class MonitoringNotificationTestJSON(base.BaseMonitoringTest):
    _interface = 'json'

    @classmethod
    def setUpClass(cls):
        super(MonitoringNotificationTestJSON, cls).setUpClass()

    @test.attr(type="gate")
    def test_create_notification(self):
        # Test case to check if new notification is created successfully.
        notification_name = data_utils.rand_name('notification-')
        notification_type = 'EMAIL'
        u_address = 'hpclmon@gmail.com'
        
        resp, body = self.monitoring_client.create_notification(name = notification_name, type=notification_type, address=u_address)
        self.assertEqual(201, resp.status)
        self.assertEqual(notification_name, body['name'])
        notification_id = body['id']
        # Delete notification
        resp, body = self.monitoring_client.delete_notification(notification_id)
        self.assertEqual(204, resp.status)

    @test.attr(type="gate")
    def test_get_notification(self):
        # Test case to check if getting notification is  successful.
        # Create notification first
        notification_name = data_utils.rand_name('notification-')
        notification_type = 'EMAIL'
        u_address = 'hpclmon@gmail.com'

        resp, body = self.monitoring_client.create_notification(name=notification_name, type=notification_type, address=u_address)
        self.assertEqual(201, resp.status)
        self.assertEqual(notification_name, body['name'])
        notification_id = body['id']
        # Get notification
        resp, body = self.monitoring_client.get_notification(notification_id)
        self.assertEqual(200, resp.status)
        self.assertIn(notification_name, body['name'])
        # Delete notification
        resp, body = self.monitoring_client.delete_notification(notification_id)
        self.assertEqual(204, resp.status)

    @test.attr(type="gate")
    def test_update_notification_name(self):
        # Test case to check if getting notification is  successful.
        # Create notification first
        notification_name = data_utils.rand_name('notification-')
        notification_type = 'EMAIL'
        u_address = 'hpclmon@gmail.com'

        resp, body = self.monitoring_client.create_notification(name=notification_name, type=notification_type, address=u_address)
        self.assertEqual(201, resp.status)
        self.assertEqual(notification_name, body['name'])
        notification_id = body['id']
        # Update notification
        new_name = notification_name + 'update'
        resp, body = self.monitoring_client.update_notification_name(
                          notification_id, name=new_name, type=notification_type, address=u_address)
        self.assertEqual(200, resp.status)
        self.assertIn(new_name, body['name'])
        # Delete notification
        resp, body = self.monitoring_client.delete_notification(notification_id)
        self.assertEqual(204, resp.status)

    @test.attr(type="gate")
    def test_update_notification_type(self):
        # Test case to check if getting notification is  successful.
        # Create notification first
        notification_name = data_utils.rand_name('notification-')
        notification_type = 'EMAIL'
        u_address = 'hpclmon@gmail.com'

        resp, body = self.monitoring_client.create_notification(name=notification_name, type=notification_type, address=u_address)
        self.assertEqual(201, resp.status)
        self.assertEqual(notification_name, body['name'])
        notification_id = body['id']
        # Update notification
        new_type = 'SMS'
        resp, body = self.monitoring_client.update_notification_type(
                          notification_id, type=new_type, name=notification_name, address=u_address)
        self.assertEqual(200, resp.status)
        self.assertIn(new_type, body['type'])
        # Delete notification
        resp, body = self.monitoring_client.delete_notification(notification_id)
        self.assertEqual(204, resp.status)

    @test.attr(type="gate")
    def test_update_notification_address(self):
        # Test case to check if getting notification is  successful.
        # Create notification first
        notification_name = data_utils.rand_name('notification-')
        notification_type = 'EMAIL'
        u_address = 'hpclmon@gmail.com'

        resp, body = self.monitoring_client.create_notification(name=notification_name, type=notification_type, address=u_address)
        self.assertEqual(201, resp.status)
        self.assertEqual(notification_name, body['name'])
        notification_id = body['id']
        # Update notification
        new_address = 'test@test.com'
        resp, body = self.monitoring_client.update_notification_address(
                          notification_id, address=new_address, name=notification_name, type=notification_type)
        self.assertEqual(200, resp.status)
        self.assertIn(new_address, body['address'])
        # Delete notification
        resp, body = self.monitoring_client.delete_notification(notification_id)
        self.assertEqual(204, resp.status)

    @test.attr(type="gate")
    def test_notification_list(self):
        # List notifications
        resp, body = self.monitoring_client.list_notifications()
        self.assertEqual(200, resp.status)

