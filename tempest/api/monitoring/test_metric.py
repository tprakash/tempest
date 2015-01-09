#
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
import time

class MonitoringMetricTestJSON(base.BaseMonitoringTest):
    _interface = 'json'

    @classmethod
    def setUpClass(cls):
        super(MonitoringMetricTestJSON, cls).setUpClass()

    @test.attr(type="gate")
    def test_metric_list_no_option(self):
        # List metric w/o parameters
        resp, body = self.monitoring_client.list_metric_no_option()
        self.assertEqual(200, resp.status)

    @test.attr(type="gate")
    def test_metric_list_by_name(self):
        # List metric by metric name
        m_name = 'thread_count'
        resp, body = self.monitoring_client.list_metric_by_name(m_name)
        self.assertEqual(200, resp.status)

    @test.attr(type="gate")
    def test_create_metric_required_option(self):
        # Create a single metric with only required parameters
        m_name = data_utils.rand_name('metric')
        m_value = 1.0 
        resp, body = self.monitoring_client.create_metric(name=m_name, value=m_value)
        self.assertEqual(204, resp.status)
        # Get metric
        resp, body = self.monitoring_client.list_metric(name=m_name)
        self.assertEqual(200, resp.status)

    @test.attr(type="gate")
    def test_create_metric_options(self):
        # Create a single metric with optional 
        m_name = data_utils.rand_name('metric')
        m_value = 1.0
        m_dimension = {
                      'key1': 'value1',
                      'key2': 'value2'
                      }
        m_timestamp = int(time.time() - 100)
        resp, body = self.monitoring_client.create_metric(
                     name=m_name, m_value=m_value, dimensions=m_dimension,timestamp=m_timestamp)
        self.assertEqual(204, resp.status)
        # Get metric
        resp, body = self.monitoring_client.list_metric(name=m_name, dimensions=m_dimension)
        self.assertEqual(200, resp.status)

    @test.attr(type="gate")
    def test_create_multiple_metric(self):
        # Create multiple metrics 
        m_name1 = data_utils.rand_name('metric')
        m_value1 = 1.0
        m_name2 = data_utils.rand_name('metric')
        m_value2 = 1.0
        m_dimension2 = {
                      'key1': 'value1',
                      'key2': 'value2'
                      }
        m_timestamp2 = int(time.time() - 100)
        resp, body = self.monitoring_client.create_multiple_metric(name1=m_name1, m_value1=m_value1,
                     name2=m_name2, m_value2=m_value2,dimensions2=m_dimension2,timestamp2=m_timestamp2)
        self.assertEqual(204, resp.status)

    @test.attr(type="gate")
    def test_metric_list(self):
        # List metric w/o parameters
        resp, body = self.monitoring_client.list_metric()
        self.assertEqual(200, resp.status)
        
    @test.attr(type="gate")
    def test_create_metric_special_char(self):
        # Create a single metric with only required parameters
        m_name = data_utils.rand_name('metric') + '!@#$%^&*()'
        m_value = 1.0 
        resp, body = self.monitoring_client.create_metric(name=m_name, value=m_value)
        self.assertEqual(204, resp.status)
        # Get metric
        resp, body = self.monitoring_client.list_metric(name=m_name)
        self.assertEqual(200, resp.status)

