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

import time
import datetime
from tempest.api.monitoring import base
from tempest.common.utils import data_utils
from tempest import exceptions
from tempest import test



class MonitoringAlarmingAPITestJSON(base.BaseMonitoringTest):
    _interface = 'json'

    @classmethod
    def setUpClass(cls):
        super(MonitoringAlarmingAPITestJSON, cls).setUpClass()
        # cls.rule = {'expression':'mem_total_mb > 0'}
        for i in range(1):
            cls.create_alarm_definition(expression="avg(cpu.idle_perc{service=monitoring}) >= 10")

    @test.attr(type="gate")
    def test_alarm_definition_list(self):
        # Test to check if all alarms definitions are listed
        # List alarms
        resp, alarm_def_list = self.monitoring_client.list_alarm_definitions()
        self.assertEqual(200, resp.status)

        # Verify created alarm in the list
        fetched_ids = [a['id'] for a in alarm_def_list]
        missing_alarms = [a for a in self.alarm_def_ids if a not in fetched_ids]
        self.assertEqual(0, len(missing_alarms),
                         "Failed to find the following created alarm(s)"
                         " in a fetched list: %s" %
                         ', '.join(str(a) for a in missing_alarms))

    @test.attr(type="gate")
    def test_create_alarm_definition_without_notification(self):
        # Test to check if a new alarm definition is created
        # Create an alarm definition
        alarm_def_name = data_utils.rand_name('monitoring_alarm_definition')
        resp, body = self.monitoring_client.create_alarm_definition(name=alarm_def_name, expression="max(cpu.system_perc) > 0")
        self.assertEqual(201, resp.status)
        self.assertEqual(alarm_def_name, body['name'])
        alarm_def_id = body['id']
        self.assertEqual("max(cpu.system_perc) > 0", body['expression'])
        # Delete alarm and verify if deleted
        resp, body = self.monitoring_client.delete_alarm_definition(alarm_def_id)
        self.assertEqual(204, resp.status)
        self.assertRaises(exceptions.NotFound,
                          self.monitoring_client.get_alarm_definition, alarm_def_id)

    @test.attr(type="gate")
    def test_get_alarm_definition(self):
        # Test to check if an alarm definition with specific alarm definition id is listed
        # Create an alarm definition
        alarm_def_name = data_utils.rand_name('monitoring_alarm_definition')
        resp, body = self.monitoring_client.create_alarm_definition(name=alarm_def_name, expression="max(cpu.system_perc) > 0")
        self.assertEqual(201, resp.status)
        self.assertEqual(alarm_def_name, body['name'])
        alarm_def_id = body['id']
        self.assertEqual("max(cpu.system_perc) > 0", body['expression'])
        # Get and verify details of an alarm definition
        resp, body = self.monitoring_client.get_alarm_definition(alarm_def_id)
        self.assertEqual(200, resp.status)
        self.assertEqual(alarm_def_name, body['name'])
        self.assertEqual("max(cpu.system_perc) > 0", body['expression'])
        # Delete alarm defintion and verify if deleted
        resp, _ = self.monitoring_client.delete_alarm_definition(alarm_def_id)
        self.assertEqual(204, resp.status)
        self.assertRaises(exceptions.NotFound,
                          self.monitoring_client.get_alarm_definition, alarm_def_id)

    @test.attr(type="gate")
    def test_update_alarm_definition(self):
        # Create an alarm definition
        alarm_def_name = data_utils.rand_name('monitoring_alarm_definition')
        resp, body = self.monitoring_client.create_alarm_definition(name=alarm_def_name, expression="mem_total_mb > 0")
        self.assertEqual(201, resp.status)
        self.assertEqual(alarm_def_name, body['name'])
        alarm_def_id = body['id']
        self.assertEqual("mem_total_mb > 0", body['expression'])
        #Update alarm
        alarm_def_name = data_utils.rand_name('monitoring_alarm_def_update')
        resp, body = self.monitoring_client.update_alarm_definition(
            alarm_def_id,
            name = alarm_def_name,
            expression = "cpu_perc < 0",
            actions_enabled = 'true',
        )
        self.assertEqual(200, resp.status)
        self.assertEqual(alarm_def_name, body['name'])
        self.assertEqual("cpu_perc < 0", body['expression'])
        # Get and verify details of an alarm definition after update
        resp, body = self.monitoring_client.get_alarm_definition(alarm_def_id)
        self.assertEqual(200, resp.status)
        self.assertEqual(alarm_def_name, body['name'])
        self.assertEqual("cpu_perc < 0", body['expression'])
        # Delete alarm defintion and verify if deleted
        resp, _ = self.monitoring_client.delete_alarm_definition(alarm_def_id)
        self.assertEqual(204, resp.status)
        self.assertRaises(exceptions.NotFound,
                          self.monitoring_client.get_alarm_definition, alarm_def_id)

    @test.attr(type="gate")
    def test_create_alarm_definition_with_notification(self):
        # Test case to create alarm definition with notification method
        notification_name = data_utils.rand_name('notification-')
        notification_type = 'EMAIL'
        u_address = 'root@localhost'

        resp, body = self.monitoring_client.create_notification(notification_name, type=notification_type, address=u_address)
        self.assertEqual(201, resp.status)
        self.assertEqual(notification_name, body['name'])
        notification_id = body['id']

        # Create an alarm definition
        alarm_def_name = data_utils.rand_name('monitoring_alarm_definition')
        resp, body = self.monitoring_client.create_alarm_definition(name=alarm_def_name,
                                                         expression="mem_total_mb > 0",
                                                         alarm_actions = notification_id,
                                                         ok_actions = notification_id,
                                                         severity="LOW")
        self.assertEqual(201, resp.status)
        self.assertEqual(alarm_def_name, body['name'])
        alarm_def_id = body['id']
        self.assertEqual("mem_total_mb > 0", body['expression'])

        # Delete alarm definition and verify if deleted
        resp, body = self.monitoring_client.delete_alarm_definition(alarm_def_id)
        self.assertEqual(204, resp.status)
        self.assertRaises(exceptions.NotFound,
                          self.monitoring_client.get_alarm_definition, alarm_def_id)

        # Delete notification
        resp, body = self.monitoring_client.delete_notification(notification_id)
        self.assertEqual(204, resp.status)

    @test.attr(type="gate")
    def test_create_alarm_definition_with_multiple_notification(self):
        # Test case to create alarm definition with notification method
        notification_name1 = data_utils.rand_name('notification-')
        notification_type1 = 'EMAIL'
        address1 = 'root@localhost'

        notification_name2 = data_utils.rand_name('notification-')
        notification_type2 = 'SMS'
        address2 = '9945039580'

        resp, body = self.monitoring_client.create_notification(notification_name1, type=notification_type1, address=address1)
        self.assertEqual(201, resp.status)
        self.assertEqual(notification_name1, body['name'])
        notification_id1 = body['id']

        resp, body = self.monitoring_client.create_notification(notification_name2, type=notification_type2, address=address2)
        self.assertEqual(201, resp.status)
        self.assertEqual(notification_name2, body['name'])
        notification_id2 = body['id']

        # Create an alarm definition
        alarm_def_name = data_utils.rand_name('monitoring_alarm_definition')
        resp, body = self.monitoring_client.create_alarm_definition(name=alarm_def_name,
                                                         expression="mem_total_mb > 0",
                                                         alarm_actions = [notification_id1, notification_id2],
                                                         ok_actions = [notification_id1, notification_id2],
                                                         severity="LOW")
        self.assertEqual(201, resp.status)
        self.assertEqual(alarm_def_name, body['name'])
        alarm_def_id = body['id']
        self.assertEqual("mem_total_mb > 0", body['expression'])

        # Delete alarm definition and verify if deleted
        resp, body = self.monitoring_client.delete_alarm_definition(alarm_def_id)
        self.assertEqual(204, resp.status)
        self.assertRaises(exceptions.NotFound,
                          self.monitoring_client.get_alarm_definition, alarm_def_id)

        # Delete notification
        resp, body = self.monitoring_client.delete_notification(notification_id1)
        self.assertEqual(204, resp.status)

        # Delete notification
        resp, body = self.monitoring_client.delete_notification(notification_id2)
        self.assertEqual(204, resp.status)

    @test.attr(type="gate")
    def test_update_notification_in_alarm_definition(self):
        # Test case to create alarm definition with notification method
        notification_name = data_utils.rand_name('notification-')
        notification_type = 'EMAIL'
        u_address = 'root@localhost'

        resp, body = self.monitoring_client.create_notification(notification_name, type=notification_type, address=u_address)
        self.assertEqual(201, resp.status)
        self.assertEqual(notification_name, body['name'])
        notification_id = body['id']

        # Create an alarm
        alarm_def_name = data_utils.rand_name('monitoring_alarm_definition')
        resp, body = self.monitoring_client.create_alarm_definition(name=alarm_def_name, expression="mem_total_mb > 0")
        self.assertEqual(201, resp.status)
        self.assertEqual(alarm_def_name, body['name'])
        alarm_def_id = body['id']
        self.assertEqual("mem_total_mb > 0", body['expression'])

        #Update alarm
        alarm_def_name = data_utils.rand_name('monitoring_alarm_update')
        resp, body = self.monitoring_client.update_alarm_definition(
            alarm_def_id,
            name = alarm_def_name,
            expression = "cpu_perc < 0",
            actions_enabled = 'true',
            alarm_actions = notification_id,
            ok_actions = notification_id
        )
        self.assertEqual(200, resp.status)
        self.assertEqual(alarm_def_name, body['name'])
        self.assertEqual("cpu_perc < 0", body['expression'])

        # Get and verify details of an alarm after update
        resp, body = self.monitoring_client.get_alarm_definition(alarm_def_id)
        self.assertEqual(200, resp.status)
        self.assertEqual(alarm_def_name, body['name'])
        self.assertEqual("cpu_perc < 0", body['expression'])

        # Delete alarm and verify if deleted
        resp, _ = self.monitoring_client.delete_alarm_definition(alarm_def_id)
        self.assertEqual(204, resp.status)
        self.assertRaises(exceptions.NotFound,
                          self.monitoring_client.get_alarm_definition, alarm_def_id)

        # Delete notification
        resp, body = self.monitoring_client.delete_notification(notification_id)
        self.assertEqual(204, resp.status)

    @test.attr(type="gate")
    def test_create_alarm_definition_with_url_in_expression(self):
        # Test case to create alarm definition with notification method
        notification_name = data_utils.rand_name('notification-')
        notification_type = 'EMAIL'
        u_address = 'root@localhost'

        resp, body = self.monitoring_client.create_notification(notification_name, type=notification_type, address=u_address)
        self.assertEqual(201, resp.status)
        self.assertEqual(notification_name, body['name'])
        notification_id = body['id']

        # Create an alarm definition
        alarm_def_name = data_utils.rand_name('monitoring_alarm_definition')
        resp, body = self.monitoring_client.create_alarm_definition(name=alarm_def_name,
                                                         expression="avg(mem_total_mb{url=https://www.google.com}) gt 0",
                                                         alarm_actions = notification_id,
                                                         ok_actions = notification_id,
                                                         severity="LOW")
        self.assertEqual(201, resp.status)
        self.assertEqual(alarm_def_name, body['name'])
        alarm_def_id = body['id']
        self.assertEqual("avg(mem_total_mb{url=https://www.google.com}) gt 0", body['expression'])

        # Delete alarm and verify if deleted
        resp, body = self.monitoring_client.delete_alarm_definition(alarm_def_id)
        self.assertEqual(204, resp.status)
        self.assertRaises(exceptions.NotFound,
                          self.monitoring_client.get_alarm_definition, alarm_def_id)

        # Delete notification
        resp, body = self.monitoring_client.delete_notification(notification_id)
        self.assertEqual(204, resp.status)

    @test.attr(type="gate")
    def test_create_alarm_definition_with_specialchars_in_expression(self):
        # Test case to create alarm with notification method
        notification_name = data_utils.rand_name('notification-')
        notification_type = 'EMAIL'
        u_address = 'root@localhost'

        resp, body = self.monitoring_client.create_notification(notification_name, type=notification_type, address=u_address)
        self.assertEqual(201, resp.status)
        self.assertEqual(notification_name, body['name'])
        notification_id = body['id']

        # Create an alarm
        alarm_def_name = data_utils.rand_name('monitoring_alarm')
        resp, body = self.monitoring_client.create_alarm_definition(name=alarm_def_name,
                                                         expression="avg(mem_total_mb{dev=\usr\local\bin}) gt 0",
                                                         alarm_actions = notification_id,
                                                         ok_actions = notification_id,
                                                         severity="LOW")
        self.assertEqual(201, resp.status)
        self.assertEqual(alarm_def_name, body['name'])
        alarm_def_id = body['id']
        self.assertEqual("avg(mem_total_mb{dev=\usr\local\bin}) gt 0", body['expression'])

        # Delete alarm and verify if deleted
        resp, body = self.monitoring_client.delete_alarm_definition(alarm_def_id)
        self.assertEqual(204, resp.status)
        self.assertRaises(exceptions.NotFound,
                          self.monitoring_client.get_alarm_definition, alarm_def_id)

        # Delete notification
        resp, body = self.monitoring_client.delete_notification(notification_id)
        self.assertEqual(204, resp.status)

    @test.attr(type="gate")
    def test_create_alarm_with_specialchar_in_expression(self):
        # Test case to create alarm with notification method
        notification_name = data_utils.rand_name('notification-')
        notification_type = 'EMAIL'
        u_address = 'root@localhost'

        resp, body = self.monitoring_client.create_notification(notification_name, type=notification_type, address=u_address)
        self.assertEqual(201, resp.status)
        self.assertEqual(notification_name, body['name'])
        notification_id = body['id']

        # Create an alarm
        alarm_def_name = data_utils.rand_name('monitoring_alarm')
        resp, body = self.monitoring_client.create_alarm_definition(name=alarm_def_name,
                                                         expression="avg(mem_total_mb{dev=!@#$%^&*}) gt 0",
                                                         alarm_actions = notification_id,
                                                         ok_actions = notification_id,
                                                         severity="LOW")
        self.assertEqual(201, resp.status)
        self.assertEqual(alarm_def_name, body['name'])
        alarm_def_id = body['id']
        self.assertEqual("avg(mem_total_mb{dev=!@#$%^&*}) gt 0", body['expression'])

        # Delete alarm and verify if deleted
        resp, body = self.monitoring_client.delete_alarm_definition(alarm_def_id)
        self.assertEqual(204, resp.status)
        self.assertRaises(exceptions.NotFound,
                          self.monitoring_client.get_alarm_definition, alarm_def_id)

        # Delete notification
        resp, body = self.monitoring_client.delete_notification(notification_id)
        self.assertEqual(204, resp.status)

    @test.attr(type="gate")
    def test_list_alarm_by_def_id(self):
        # Test case to create alarm definition with notification method
        notification_name = data_utils.rand_name('notification-')
        notification_type = 'EMAIL'
        u_address = 'root@localhost'

        resp, body = self.monitoring_client.create_notification(notification_name, type=notification_type, address=u_address)
        self.assertEqual(201, resp.status)
        self.assertEqual(notification_name, body['name'])
        notification_id = body['id']

        # Create an alarm definition
        alarm_def_name = data_utils.rand_name('monitoring_alarm_definition')
        resp, body = self.monitoring_client.create_alarm_definition(name=alarm_def_name,
                                                         expression="mem_total_mb > 0",
                                                         alarm_actions = notification_id,
                                                         ok_actions = notification_id,
                                                         severity="LOW")
        self.assertEqual(201, resp.status)
        self.assertEqual(alarm_def_name, body['name'])
        alarm_def_id = body['id']
        self.assertEqual("mem_total_mb > 0", body['expression'])

        time.sleep(60)
        # List alarm using alarm definition id
        resp, body = self.monitoring_client.get_alarms_by_def_id(alarm_def_id)
        self.assertEqual(200, resp.status)

        # Delete alarm definition and verify if deleted
        resp, body = self.monitoring_client.delete_alarm_definition(alarm_def_id)
        self.assertEqual(204, resp.status)
        self.assertRaises(exceptions.NotFound,
                          self.monitoring_client.get_alarm_definition, alarm_def_id)

        # Delete notification
        resp, body = self.monitoring_client.delete_notification(notification_id)
        self.assertEqual(204, resp.status)


    @test.attr(type="gate")
    def test_list_alarm_by_metric_name(self):
        # Test case to create alarm definition with notification method
        notification_name = data_utils.rand_name('notification-')
        notification_type = 'EMAIL'
        u_address = 'root@localhost'

        resp, body = self.monitoring_client.create_notification(notification_name, type=notification_type, address=u_address)
        self.assertEqual(201, resp.status)
        self.assertEqual(notification_name, body['name'])
        notification_id = body['id']

        # Create an alarm definition
        alarm_def_name = data_utils.rand_name('monitoring_alarm_definition')
        resp, body = self.monitoring_client.create_alarm_definition(name=alarm_def_name,
                                                         expression="cpu.system_perc > 0",
                                                         alarm_actions = notification_id,
                                                         ok_actions = notification_id,
                                                         severity="LOW")
        self.assertEqual(201, resp.status)
        self.assertEqual(alarm_def_name, body['name'])
        alarm_def_id = body['id']
        self.assertEqual("cpu.system_perc > 0", body['expression'])

        time.sleep(60)
        # List alarm using metric name
        resp, body = self.monitoring_client.get_alarms_by_metric_name("cpu.system_perc")
        self.assertEqual(200, resp.status)

        # Delete alarm definition and verify if deleted
        resp, body = self.monitoring_client.delete_alarm_definition(alarm_def_id)
        self.assertEqual(204, resp.status)
        self.assertRaises(exceptions.NotFound,
                          self.monitoring_client.get_alarm_definition, alarm_def_id)

        # Delete notification
        resp, body = self.monitoring_client.delete_notification(notification_id)
        self.assertEqual(204, resp.status)

    @test.attr(type="gate")
    def test_list_alarm_by_metric_name_and_dimension(self):
        # Test case to create alarm definition with notification method
        notification_name = data_utils.rand_name('notification-')
        notification_type = 'EMAIL'
        u_address = 'root@localhost'

        resp, body = self.monitoring_client.create_notification(notification_name, type=notification_type, address=u_address)
        self.assertEqual(201, resp.status)
        self.assertEqual(notification_name, body['name'])
        notification_id = body['id']

        # Create an alarm definition
        alarm_def_name = data_utils.rand_name('monitoring_alarm_definition')
        resp, body = self.monitoring_client.create_alarm_definition(name=alarm_def_name,
                                                         expression="cpu.system_perc > 0",
                                                         alarm_actions = notification_id,
                                                         ok_actions = notification_id,
                                                         severity="LOW")
        self.assertEqual(201, resp.status)
        self.assertEqual(alarm_def_name, body['name'])
        alarm_def_id = body['id']
        self.assertEqual("cpu.system_perc > 0", body['expression'])

        time.sleep(60)
        # List alarm using metric name
        resp, body = self.monitoring_client.get_alarms_by_metric_dimensions("cpu.system_perc","service:monitoring")
        self.assertEqual(200, resp.status)

        # Delete alarm definition and verify if deleted
        resp, body = self.monitoring_client.delete_alarm_definition(alarm_def_id)
        self.assertEqual(204, resp.status)
        self.assertRaises(exceptions.NotFound,
                          self.monitoring_client.get_alarm_definition, alarm_def_id)

        # Delete notification
        resp, body = self.monitoring_client.delete_notification(notification_id)
        self.assertEqual(204, resp.status)

    @test.attr(type="gate")
    def test_list_alarm_by_state(self):
        # Test case to create alarm definition with notification method
        notification_name = data_utils.rand_name('notification-')
        notification_type = 'EMAIL'
        u_address = 'root@localhost'

        resp, body = self.monitoring_client.create_notification(notification_name, type=notification_type, address=u_address)
        self.assertEqual(201, resp.status)
        self.assertEqual(notification_name, body['name'])
        notification_id = body['id']

        # Create an alarm definition
        alarm_def_name = data_utils.rand_name('monitoring_alarm_definition')
        resp, body = self.monitoring_client.create_alarm_definition(name=alarm_def_name,
                                                         expression="cpu.system_perc > 0",
                                                         alarm_actions = notification_id,
                                                         ok_actions = notification_id,
                                                         severity="LOW")
        self.assertEqual(201, resp.status)
        self.assertEqual(alarm_def_name, body['name'])
        alarm_def_id = body['id']
        self.assertEqual("cpu.system_perc > 0", body['expression'])

        time.sleep(120)
        # List alarm using state
        resp, body = self.monitoring_client.get_alarms_by_state(alarm_def_id, "ALARM")
        self.assertEqual(200, resp.status)

        # Delete alarm definition and verify if deleted
        resp, body = self.monitoring_client.delete_alarm_definition(alarm_def_id)
        self.assertEqual(204, resp.status)
        self.assertRaises(exceptions.NotFound,
                          self.monitoring_client.get_alarm_definition, alarm_def_id)

        # Delete notification
        resp, body = self.monitoring_client.delete_notification(notification_id)
        self.assertEqual(204, resp.status)

    @test.attr(type="gate")
    def test_get_delete_the_specified_alarm(self):
        # create alarm definition with notification method
        notification_name = data_utils.rand_name('notification-')
        notification_type = 'EMAIL'
        u_address = 'root@localhost'

        resp, body = self.monitoring_client.create_notification(notification_name, type=notification_type, address=u_address)
        self.assertEqual(201, resp.status)
        self.assertEqual(notification_name, body['name'])
        notification_id = body['id']

        # Create an alarm definition
        alarm_def_name = data_utils.rand_name('monitoring_alarm_definition')
        resp, body = self.monitoring_client.create_alarm_definition(name=alarm_def_name,
                                                         expression="cpu.system_perc > 0",
                                                         alarm_actions = notification_id,
                                                         ok_actions = notification_id,
                                                         severity="LOW")
        self.assertEqual(201, resp.status)
        self.assertEqual(alarm_def_name, body['name'])
        alarm_def_id = body['id']
        self.assertEqual("cpu.system_perc > 0", body['expression'])

        time.sleep(60)
        # List alarm using alarm def id
        resp, body = self.monitoring_client.get_alarms_by_def_id(alarm_def_id)
        self.assertEqual(200, resp.status)
        alarm_id = body[0]['id']

        # List specific alarm
        resp, body = self.monitoring_client.get_alarm(alarm_id)
        self.assertRaises(exceptions.NotFound,
                          self.monitoring_client.get_alarm, alarm_id)
        self.assertEqual(200, resp.status)

        # Delete alarm and verify if deleted
        resp, body = self.monitoring_client.delete_alarm(alarm_id)
        self.assertEqual(204, resp.status)
        self.assertRaises(exceptions.NotFound,
                          self.monitoring_client.get_alarm, alarm_id)

        # Delete alarm definition and verify if deleted
        resp, body = self.monitoring_client.delete_alarm_definition(alarm_def_id)
        self.assertEqual(204, resp.status)
        self.assertRaises(exceptions.NotFound,
                          self.monitoring_client.get_alarm_definition, alarm_def_id)

        # Delete notification
        resp, body = self.monitoring_client.delete_notification(notification_id)
        self.assertEqual(204, resp.status)

    @test.attr(type="gate")
    def test_update_the_specified_alarm(self):
        # create alarm definition with notification method
        notification_name = data_utils.rand_name('notification-')
        notification_type = 'EMAIL'
        u_address = 'root@localhost'

        resp, body = self.monitoring_client.create_notification(notification_name, type=notification_type, address=u_address)
        self.assertEqual(201, resp.status)
        self.assertEqual(notification_name, body['name'])
        notification_id = body['id']

        # Create an alarm definition
        alarm_def_name = data_utils.rand_name('monitoring_alarm_definition')
        resp, body = self.monitoring_client.create_alarm_definition(name=alarm_def_name,
                                                         expression="cpu.system_perc > 0",
                                                         alarm_actions = notification_id,
                                                         ok_actions = notification_id,
                                                         severity="LOW")
        self.assertEqual(201, resp.status)
        self.assertEqual(alarm_def_name, body['name'])
        alarm_def_id = body['id']
        self.assertEqual("cpu.system_perc > 0", body['expression'])

        time.sleep(60)
        # List alarm using alarm def id
        resp, body = self.monitoring_client.get_alarms_by_def_id(alarm_def_id)
        self.assertEqual(200, resp.status)
        alarm_id = body[0]['id']

        # Update specific alarm
        resp, body = self.monitoring_client.update_alarm(alarm_id, state="OK")
        self.assertEqual(200, resp.status)


        # Delete alarm definition and verify if deleted
        resp, body = self.monitoring_client.delete_alarm_definition(alarm_def_id)
        self.assertEqual(204, resp.status)
        self.assertRaises(exceptions.NotFound,
                          self.monitoring_client.get_alarm_definition, alarm_def_id)

        # Delete notification
        resp, body = self.monitoring_client.delete_notification(notification_id)
        self.assertEqual(204, resp.status)

    @test.attr(type="gate")
    def test_alarms_history_state(self):
        # create alarm definition with notification method
        notification_name = data_utils.rand_name('notification-')
        notification_type = 'EMAIL'
        u_address = 'root@localhost'

        resp, body = self.monitoring_client.create_notification(notification_name, type=notification_type, address=u_address)
        self.assertEqual(201, resp.status)
        self.assertEqual(notification_name, body['name'])
        notification_id = body['id']

        # Create an alarm definition
        alarm_def_name = data_utils.rand_name('monitoring_alarm_definition')
        resp, body = self.monitoring_client.create_alarm_definition(name=alarm_def_name,
                                                         expression="cpu.system_perc > 0",
                                                         alarm_actions = notification_id,
                                                         ok_actions = notification_id,
                                                         severity="LOW")
        self.assertEqual(201, resp.status)
        self.assertEqual(alarm_def_name, body['name'])
        alarm_def_id = body['id']
        self.assertEqual("cpu.system_perc > 0", body['expression'])

        time.sleep(70)
        # List alarm using alarm def id
        resp, body = self.monitoring_client.get_alarms_by_def_id(alarm_def_id)
        self.assertEqual(200, resp.status)
        alarm_id = body[0]['id']

        # Update specific alarm
        resp, body = self.monitoring_client.update_alarm(alarm_id, state="OK")
        self.assertEqual(200, resp.status)
        time.sleep(70)

        # Get alarms state history
        resp, body = self.monitoring_client.get_alarms_state_history_by_dimensions("service:monitoring")
        self.assertEqual(200, resp.status)
        self.assertTrue('old_state' in body[0].keys(), body[0].keys())
        self.assertTrue('new_state' in body[0].keys(), body[0].keys())

        # Delete alarm definition and verify if deleted
        resp, body = self.monitoring_client.delete_alarm_definition(alarm_def_id)
        self.assertEqual(204, resp.status)
        self.assertRaises(exceptions.NotFound,
                          self.monitoring_client.get_alarm_definition, alarm_def_id)

        # Delete notification
        resp, body = self.monitoring_client.delete_notification(notification_id)
        self.assertEqual(204, resp.status)

    @test.attr(type="gate")
    def test_alarms_history_state_by_start_end_time(self):
        # create alarm definition with notification method
        notification_name = data_utils.rand_name('notification-')
        notification_type = 'EMAIL'
        u_address = 'root@localhost'

        resp, body = self.monitoring_client.create_notification(notification_name, type=notification_type, address=u_address)
        self.assertEqual(201, resp.status)
        self.assertEqual(notification_name, body['name'])
        notification_id = body['id']

        # Create an alarm definition
        alarm_def_name = data_utils.rand_name('monitoring_alarm_definition')
        resp, body = self.monitoring_client.create_alarm_definition(name=alarm_def_name,
                                                         expression="cpu.system_perc > 0",
                                                         alarm_actions = notification_id,
                                                         ok_actions = notification_id,
                                                         severity="LOW")
        self.assertEqual(201, resp.status)
        self.assertEqual(alarm_def_name, body['name'])
        alarm_def_id = body['id']
        self.assertEqual("cpu.system_perc > 0", body['expression'])

        time.sleep(70)
        # List alarm using alarm def id
        resp, body = self.monitoring_client.get_alarms_by_def_id(alarm_def_id)
        self.assertEqual(200, resp.status)
        print body
        alarm_id = body[0]['id']

        # Update specific alarm
        resp, body = self.monitoring_client.update_alarm(alarm_id, state="OK")
        self.assertEqual(200, resp.status)
        time.sleep(70)

        # Get alarms state history
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        current_time = current_time.replace(' ', 'T') + 'Z'
        resp, body = self.monitoring_client.get_alarms_state_history_by_dimensions_and_time(dimensions="service:monitoring", end_time=current_time)
        self.assertEqual(200, resp.status)

        # Delete alarm definition and verify if deleted
        resp, body = self.monitoring_client.delete_alarm_definition(alarm_def_id)
        self.assertEqual(204, resp.status)
        self.assertRaises(exceptions.NotFound,
                          self.monitoring_client.get_alarm_definition, alarm_def_id)

        # Delete notification
        resp, body = self.monitoring_client.delete_notification(notification_id)
        self.assertEqual(204, resp.status)

    @test.attr(type="gate")
    def test_alarm_history_state_by_alarm_id(self):
        # create alarm definition with notification method
        notification_name = data_utils.rand_name('notification-')
        notification_type = 'EMAIL'
        u_address = 'root@localhost'

        resp, body = self.monitoring_client.create_notification(notification_name, type=notification_type, address=u_address)
        self.assertEqual(201, resp.status)
        self.assertEqual(notification_name, body['name'])
        notification_id = body['id']

        # Create an alarm definition
        alarm_def_name = data_utils.rand_name('monitoring_alarm_definition')
        resp, body = self.monitoring_client.create_alarm_definition(name=alarm_def_name,
                                                         expression="cpu.system_perc > 0",
                                                         alarm_actions = notification_id,
                                                         ok_actions = notification_id,
                                                         severity="LOW")
        self.assertEqual(201, resp.status)
        self.assertEqual(alarm_def_name, body['name'])
        alarm_def_id = body['id']
        self.assertEqual("cpu.system_perc > 0", body['expression'])

        time.sleep(70)
        # List alarm using alarm def id
        resp, body = self.monitoring_client.get_alarms_by_def_id(alarm_def_id)
        self.assertEqual(200, resp.status)
        alarm_id = body[0]['id']

        # Update specific alarm
        resp, body = self.monitoring_client.update_alarm(alarm_id, state="OK")
        self.assertEqual(200, resp.status)
        time.sleep(70)

        # Get alarms state history
        resp, body = self.monitoring_client.get_alarm_state_history_by_alarm_id(alarm_id)
        self.assertEqual(200, resp.status)
        self.assertTrue('old_state' in body[0].keys(), body[0].keys())
        self.assertTrue('new_state' in body[0].keys(), body[0].keys())

        # Delete alarm definition and verify if deleted
        resp, body = self.monitoring_client.delete_alarm_definition(alarm_def_id)
        self.assertEqual(204, resp.status)
        self.assertRaises(exceptions.NotFound,
                          self.monitoring_client.get_alarm_definition, alarm_def_id)

        # Delete notification
        resp, body = self.monitoring_client.delete_notification(notification_id)
        self.assertEqual(204, resp.status)

    @classmethod
    def resource_cleanup(cls):
        super(MonitoringAlarmingAPITestJSON, cls).resource_cleanup()
