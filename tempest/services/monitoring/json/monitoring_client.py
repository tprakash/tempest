# Copyright 2014 OpenStack Foundation
# All Rights Reserved.
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

import urllib
import time
import datetime
from tempest.common import rest_client
from tempest import config
from tempest.openstack.common import jsonutils as json
# import tempest.services.monitoring.monitoring_client_base as client

CONF = config.CONF

class MonitoringClientJSON(rest_client.RestClient):

    def __init__(self, auth_provider):
        super(MonitoringClientJSON, self).__init__(
            auth_provider,
            CONF.monitoring.catalog_type,
            CONF.identity.region,
            endpoint_type=CONF.monitoring.endpoint_type)
        self.version = '2.0'
        self.uri_prefix = "v%s" % self.version

    # def get_rest_client(self, auth_provider):
    #     return rest_client.RestClient(auth_provider)

    def deserialize(self, body):
        return json.loads(body.replace("\n", ""))

    def serialize(self, body):
        return json.dumps(body)

    # def post(self, uri, body):
    #     body = self.serialize(body)
    #     resp, body = self.post(uri, body)
    #     body = self.deserialize(body)
    #     return resp, body

    # def put(self, uri, body):
    #     body = self.serialize(body)
    #     resp, body = self.put(uri, body)
    #     body = self.deserialize(body)
    #     return resp, body

    # def get(self, uri):
    #     resp, body = self.get(uri)
    #     body = self.deserialize(body)
    #     return resp, body

    # def delete(self, uri):
    #     resp, body = self.delete(uri)
    #     if body:
    #         body = self.deserialize(body)
    #     return resp, body

    # def patch(self, uri, body):
    #     body = self.serialize(body)
    #     resp, body = self.patch(uri, body)
    #     body = self.deserialize(body)
    #     return resp, body

    def helper_list(self, uri, query=None, period=None):
        uri_dict = {}
        if query:
            uri_dict = {'q.field': query[0],
                        'q.op': query[1],
                        'q.value': query[2]}
        if period:
            uri_dict['period'] = period
        if uri_dict:
            uri += "?%s" % urllib.urlencode(uri_dict)
        return self.get(uri)

    def create_alarm_definition(self, **kwargs):
        uri = "/alarm-definitions/"
        return self.post(uri, kwargs)

    def list_alarm_definitions(self, query=None):
        uri = '/alarm-definitions'
        return self.helper_list(uri, query)

    def get_alarm_definition(self, alarm_def_id):
        uri = '/alarm-definitions/%s' % alarm_def_id
        return self.get(uri)

    def update_alarm_definition(self, alarm_def_id, **kwargs):
        uri = "/alarm-definitions/%s" % alarm_def_id
        return self.put(uri, kwargs)

    def patch_alarm_definition(self, alarm_def_id, **kwargs):
        uri = "/alarm-definitions/%s" % alarm_def_id
        return self.patch(uri, kwargs)

    def delete_alarm_definition(self, alarm_def_id):
        uri = "/alarm-definitions/%s" % alarm_def_id
        return self.delete(uri)

    def list_alarms(self, query=None):
        uri = '/alarms'
        return self.helper_list(uri, query)

    def get_alarm(self, alarm_id):
        uri = '/alarms/%s' % alarm_id
        return self.get(uri)

    def update_alarm(self, alarm_id, **kwargs):
        uri = "/alarms/%s" % alarm_id
        return self.put(uri, kwargs)

    def patch_alarm(self, alarm_id, **kwargs):
        uri = "/alarms/%s" % alarm_id
        return self.patch(uri, kwargs)

    def delete_alarm(self, alarm_id):
        uri = "/alarms/%s" % alarm_id
        return self.delete(uri)

    def get_alarms_by_def_id(self, alarm_def_id):
        uri = '/alarms?alarm_definition_id=' + alarm_def_id
        return self.get(uri)

    def get_alarms_by_metric_name(self, metric_name):
        uri = '/alarms?metric_name=' + metric_name
        return self.get(uri)

    def get_alarms_by_metric_dimensions(self, metric_name, metric_dimensions):
        uri = '/alarms?metric_name=' + metric_name + '&metric_dimensions=' + metric_dimensions
        return self.get(uri)

    def get_alarms_by_state(self, alarm_def_id, state):
        uri = '/alarms?alarm_definition_id=' + alarm_def_id + '&state=' + state
        return self.get(uri)

    def get_alarms_state_history_by_dimensions(self, metric_dimensions):
        uri = '/alarms/state-history?dimensions=' + metric_dimensions
        return self.get(uri)

    def get_alarms_state_history_by_dimensions_and_time(self, **kwargs):
        uri = '/alarms/state-history'
        default_starttime = (datetime.datetime.now() - datetime.timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
        default_starttime = default_starttime.replace(' ', 'T') + 'Z'
        m_dimension = kwargs.get('dimensions', None)
        m_start_time = kwargs.get('start_time', default_starttime)
        m_end_time = kwargs.get('end_time', None)
        if m_dimension is not None:
            uri += '?dimensions=' + m_dimension
        uri += '&start_time=' + m_start_time
        if m_end_time is not None:
            uri += '&end_time=' + m_end_time
        return self.get(uri)

    def get_alarm_state_history_by_alarm_id(self, alarm_id):
        uri = "/alarms/%s/state-history" % alarm_id
        return self.get(uri)

    def list_notifications(self, query=None):
        uri = '/notification-methods'
        return self.helper_list(uri, query)

    def create_notification(self, notification_name, **kwargs):
        """Create a notification."""
        uri = '/notification-methods'
        notification_type = kwargs.get('type', None)
        address = kwargs.get('address', None)
        post_body = {
            'name': notification_name,
            'type': notification_type,
            'address': address
        }
        post_body = json.dumps(post_body)
        resp, body = self.post(uri, post_body)
        # resp, body = self.post(url, post_body)
        body = self.deserialize(body)
        return resp, body

    def delete_notification(self, notification_id):
        """Delete a notification."""
        uri = '/notification-methods/' + notification_id
        resp, body = self.delete(uri)
        # resp, body = self.delete(uri)
        return resp, body

    def get_notification(self, notification_id):
        """Get specific notification"""
        uri = '/notification-methods/' + notification_id
        resp, body = self.get(uri)
        return resp, body

    def update_notification_name(self, notification_id, notification_name, **kwargs):
        """Update a notification."""
        url = '/notification-methods/' + notification_id
        notification_type = kwargs.get('type', None)
        address = kwargs.get('address', None)
        post_body = {
            'name': notification_name,
            'type': notification_type,
            'address': address
        }
        post_body = json.dumps(post_body)
        resp, body = self.put(url, post_body)
        return resp, body

    def update_notification_type(self, notification_id, notification_type, **kwargs):
        """Update a notification."""
        url = '/notification-methods/' + notification_id
        notification_name = kwargs.get('name', None)
        address = kwargs.get('address', None)
        post_body = {
            'name': notification_name,
            'type': notification_type,
            'address': address
        }
        post_body = json.dumps(post_body)
        resp, body = self.put(url, post_body)
        return resp, body

    def update_notification_address(self, notification_id, address, **kwargs):
        """Update a notification."""
        url = '/notification-methods/' + notification_id
        notification_name = kwargs.get('name', None)
        notification_type = kwargs.get('type', None)
        post_body = {
            'name': notification_name,
            'type': notification_type,
            'address': address
        }
        post_body = json.dumps(post_body)
        resp, body = self.put(url, post_body)
        return resp, body

    def list_metric_no_option(self):
        """List metric w/o options."""
        url = '/metrics'
        resp, body = self.get(url)
        return resp, body

    def list_metric_by_name(self, metric_name):
        """List metric w/o options."""
        url = '/metrics?name=' + metric_name
        resp, body = self.get(url)
        return resp, body

    def list_metric(self, **kwargs):
        """List metric."""
        url = '/metrics'
        m_name = kwargs.get('name', None)
        m_dimension = kwargs.get('dimensions', None)
        if m_name is not None:
           url  += '?name=' + m_name
        if m_dimension is not None:
           keylist = m_dimension.keys()
           dimension = ''
           for index, key in enumerate(keylist):
               dimension += key + ':' + str(m_dimension.get(key))
               if index < len(keylist)-1:
                   dimension += ','
           url += '&dimensions=' + dimension
        resp, body = self.get(url)
        return resp, body


    def create_metric(self, **kwargs):
        """Create a metric."""
        url = '/metrics'
        m_name = kwargs.get('name', None)
        m_value = kwargs.get('value', None)
        m_dimension = kwargs.get('dimensions', None)
        m_timestamp = kwargs.get('timestamp', int(time.time()))
        post_body = {
            'name': m_name,
            'value': m_value,
            'dimensions': m_dimension,
            'timestamp': m_timestamp
        }
        post_body = json.dumps(post_body)
        resp, body = self.post(url, post_body)
        return resp, body

    def create_multiple_metric(self, **kwargs):
        """Create a metric."""
        url = '/metrics'
        m_name1 = kwargs.get('name1', None)
        m_value1 = kwargs.get('value1', None)
        m_dimension1 = kwargs.get('dimensions1', None)
        m_timestamp1 = kwargs.get('timestamp1', int(time.time()))
        post_body1 = {
            'name': m_name1,
            'value': m_value1,
            'dimensions': m_dimension1,
            'timestamp': m_timestamp1
        }
        post_body1 = json.dumps(post_body1)
        m_name2 = kwargs.get('name2', None)
        m_value2 = kwargs.get('value2', None)
        m_dimension2 = kwargs.get('dimensions2', None)
        m_timestamp2 = kwargs.get('timestamp2', int(time.time()))
        post_body2 = {
            'name': m_name2,
            'value': m_value2,
            'dimensions': m_dimension2,
            'timestamp': m_timestamp2
        }
        post_body2 = json.dumps(post_body2)
        m_array = '[' + post_body1 + ',' + post_body2 + ']'
        print m_array
        resp, body = self.post(url, m_array)
        return resp, body

    def get_version(self, query=None):
        """List monasca api version."""
        uri = '/'
        # resp, body = self.get(url)
        return self.helper_list(uri, query)

    def metric_measurement(self, **kwargs):
        """List a metric measurement."""
        url = '/metrics/measurements'
        default_starttime = (datetime.datetime.now() - datetime.timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S')
        default_starttime = default_starttime.replace(' ', 'T') + 'Z'
        m_name = kwargs.get('name', None)
        m_dimension = kwargs.get('dimensions', None)
        m_start_time = kwargs.get('start_time', default_starttime)
        m_end_time = kwargs.get('end_time', None)
        m_limit = kwargs.get('limit', None)
        url += '?start_time=' + m_start_time
        if m_name is not None:
            url += '&name=' + m_name
        if m_dimension is not None:
            keylist = m_dimension.keys()
            dimension = ''
            for index, key in enumerate(keylist):
                dimension += key + ':' + str(m_dimension.get(key))
                if index < len(keylist)-1:
                    dimension += ','
            url += '&dimensions=' + dimension
        if m_end_time is not None:
            url += '&end_time=' + m_end_time
        if m_limit is not None:
            url += '&limit=' + m_limit
        resp, body = self.get(url)
        return resp, body

    def metric_statistics(self, **kwargs):
        """List a metric statistics."""
        url = '/metrics/statistics'
        default_starttime = (datetime.datetime.now() - datetime.timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S')
        default_starttime = default_starttime.replace(' ', 'T') + 'Z'
        m_name = kwargs.get('name', None)
        m_dimension = kwargs.get('dimensions', None)
        m_start_time = kwargs.get('start_time', default_starttime)
        m_end_time = kwargs.get('end_time', None)
        m_statistics = kwargs.get('statistics', None)
        m_period = kwargs.get('period', 300)
        url += '?nsme=' + m_name + '&statistics=' + m_statistics + '&start_time=' + m_start_time
        if m_dimension is not None:
            keylist = m_dimension.keys()
            dimension = ''
            for index, key in enumerate(keylist):
                dimension += key + ':' + str(m_dimension.get(key))
                if index < len(keylist)-1:
                    dimension += ','
            url += '&dimensions=' + m_dimension
        if m_end_time is not None:
            url += '&end_time=' + m_end_time
        if m_period is not None:
            url += '&period=' + str(m_period)
        resp, body = self.get(url)
        return resp, body

    # def add_sample(self, sample_list, meter_name, meter_unit, volume,
    #                sample_type, resource_id, **kwargs):
    #     sample = {"counter_name": meter_name, "counter_unit": meter_unit,
    #               "counter_volume": volume, "counter_type": sample_type,
    #               "resource_id": resource_id}
    #     for key in kwargs:
    #         sample[key] = kwargs[key]
    #
    #     sample_list.append(self.serialize(sample))
    #     return sample_list
    #
    # def create_sample(self, meter_name, sample_list):
    #     uri = "%s/meters/%s" % (self.uri_prefix, meter_name)
    #     return self.post(uri, str(sample_list))
