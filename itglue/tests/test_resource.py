import unittest
from unittest.mock import patch, MagicMock

import itglue


class TestData(object):
    resource_type = 'configurations'
    resource_id = 123
    resource_name = 'ITG-MBP15-13'
    resource_alt_name = 'ITG-MBP15-21'
    resource_notes = 'Some notes'
    resource_ip = '123.456.789.10'
    parent_type = 'organizations'
    parent_name = 'Happy Frog'
    resource_class = itglue.Configuration
    data_dict = {
        'id': resource_id,
        'type': resource_type,
        'attributes': {'name': resource_alt_name}
    }
    data_list = [
        {
            'id': resource_id,
            'type': resource_type,
            'attributes': {'name': resource_alt_name}
        }
    ]
    resource_from_data = itglue.Configuration(
        id=resource_id,
        name=resource_alt_name
    )


class TestResource(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.mock_connection = MagicMock()
        patcher = patch('itglue.resources.connection', self.mock_connection)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.resource_class = itglue.Configuration
        self.parent_resource = itglue.Organization(name=TestData.parent_name)
        self.resource = itglue.Configuration(
            name=TestData.resource_name,
            notes=TestData.resource_notes
        )

    def tearDown(self):
        self.parent_resource = None
        self.resource = None

    def test_resource_type(self):
        self.assertEqual(self.resource.resource_type(), TestData.resource_type)

    def test_id(self):
        self.resource.id = TestData.resource_id
        self.assertEqual(self.resource.id, TestData.resource_id)

    def test_attributes(self):
        self.assertEqual(self.resource.attributes, {'name': TestData.resource_name, 'notes': TestData.resource_notes})

    def test_get_attr(self):
        self.assertEqual(self.resource.get_attr('name'), TestData.resource_name)
        self.assertEqual(self.resource.get_attr('notes'), TestData.resource_notes)
        self.assertEqual(self.resource.get_attr('foo'), None)

    def test_set_attr(self):
        self.assertEqual(self.resource.set_attr('primary_ip', TestData.resource_ip), TestData.resource_ip)
        self.assertEqual(self.resource.attributes['primary_ip'], TestData.resource_ip)
        self.assertEqual(self.resource.get_attr('primary_ip'), TestData.resource_ip)

    def test_set_attributes(self):
        self.resource.set_attributes(name=TestData.resource_alt_name, primary_ip=TestData.resource_ip)
        self.assertEqual(self.resource.attributes['name'], TestData.resource_alt_name)
        self.assertEqual(self.resource.attributes['primary_ip'], TestData.resource_ip)

    def test_save_new(self):
        with patch.object(itglue.resources.connection, 'post', return_value=TestData.data_dict):
            expected_path = '/{}'.format(TestData.resource_type)
            expected_payload = {
                'type': TestData.resource_type,
                'attributes': {
                    'name': TestData.resource_name,
                    'notes': TestData.resource_notes
                }
            }
            self.assertEqual(self.resource.save(), TestData.resource_from_data)
            self.mock_connection.post.assert_called_once_with(expected_path, payload=expected_payload, relationships={})

    def test_save_existing(self):
        with patch.object(itglue.resources.connection, 'patch', return_value=TestData.data_dict):
            self.resource.id = TestData.resource_id
            self.resource.set_attr('name', TestData.resource_alt_name)
            expected_path = '/{}/{}'.format(TestData.resource_type, TestData.resource_id)
            expected_payload = {
                'id': TestData.resource_id,
                'type': TestData.resource_type,
                'attributes': {
                    'name': TestData.resource_alt_name,
                    'notes': TestData.resource_notes
                }
            }
            self.assertEqual(self.resource.save(), TestData.resource_from_data)
            self.mock_connection.patch.assert_called_once_with(expected_path, payload=expected_payload)

    def test_save_with_parent(self):
        with patch.object(itglue.resources.connection, 'post', return_value=TestData.data_dict):
            self.parent_resource.id = 456
            expected_path = '/{parent_type}/{parent_id}/relationships/{resource_type}'.format(
                parent_type=self.parent_resource.resource_type(),
                parent_id=self.parent_resource.id,
                resource_type=TestData.resource_type
            )
            expected_payload = {
                'type': TestData.resource_type,
                'attributes': {
                    'name': TestData.resource_name,
                    'notes': TestData.resource_notes
                }
            }
            self.assertEqual(self.resource.save(parent=self.parent_resource), TestData.resource_from_data)
            self.mock_connection.post.assert_called_once_with(expected_path, payload=expected_payload, relationships={})

    def test_create_error(self):
        self.resource.id = TestData.resource_id
        self.assertRaises(itglue.Configuration.ResourceError, self.resource.create)

    def test_create_success(self):
        with patch.object(itglue.resources.connection, 'post', return_value=TestData.data_dict):
            expected_path = '/{}'.format(TestData.resource_type)
            expected_payload = {
                'type': TestData.resource_type,
                'attributes': {
                    'name': TestData.resource_name,
                    'notes': TestData.resource_notes
                }
            }
            self.assertEqual(self.resource.create(), TestData.resource_from_data)
            self.mock_connection.post.assert_called_once_with(expected_path, payload=expected_payload, relationships={})

    def test_create_with_relationships(self):
        with patch.object(itglue.resources.connection, 'post', return_value=TestData.data_dict):
            interface_1 = itglue.ConfigurationInterface(name='eni-545f123a', ip_address='1.2.3.4')
            interface_2 = itglue.ConfigurationInterface(name='eni-545f789a', ip_address='5.6.7.8')

            expected_path = '/{}'.format(TestData.resource_type)
            expected_payload = {
                'type': TestData.resource_type,
                'attributes': {
                    'name': TestData.resource_name,
                    'notes': TestData.resource_notes
                }
            }
            expected_rel_payload = {
                'configuration_interfaces': [
                    {
                        'type': 'configuration_interfaces',
                        'attributes': {'name': 'eni-545f123a', 'ip_address': '1.2.3.4'}
                    },
                    {
                        'type': 'configuration_interfaces',
                        'attributes': {'name': 'eni-545f789a', 'ip_address': '5.6.7.8'}
                    }
                ]
            }
            resource = self.resource.create(configuration_interfaces=[interface_1, interface_2])
            self.assertEqual(resource, TestData.resource_from_data)
            self.mock_connection.post.assert_called_once_with(
                expected_path,
                payload=expected_payload,
                relationships=expected_rel_payload
            )

    def test_update_error(self):
        self.assertRaises(itglue.Configuration.ResourceError, self.resource.update)

    def test_update_success(self):
        with patch.object(itglue.resources.connection, 'patch', return_value=TestData.data_dict):
            self.resource.id = TestData.resource_id
            self.resource.set_attr('name', TestData.resource_alt_name)
            expected_path = '/{}/{}'.format(TestData.resource_type, TestData.resource_id)
            expected_payload = {
                'id': TestData.resource_id,
                'type': TestData.resource_type,
                'attributes': {
                    'name': TestData.resource_alt_name,
                    'notes': TestData.resource_notes
                }
            }
            self.assertEqual(self.resource.update(), TestData.resource_from_data)
            self.mock_connection.patch.assert_called_once_with(expected_path, payload=expected_payload)

    def test_update_with_parent(self):
        with patch.object(itglue.resources.connection, 'patch', return_value=TestData.data_dict):
            self.parent_resource.id = 456
            self.resource.id = TestData.resource_id
            expected_path = '/{parent_type}/{parent_id}/relationships/{resource_type}/{resource_id}'.format(
                parent_type=self.parent_resource.resource_type(),
                parent_id=self.parent_resource.id,
                resource_type=TestData.resource_type,
                resource_id=TestData.resource_id
            )
            expected_payload = {
                'id': TestData.resource_id,
                'type': TestData.resource_type,
                'attributes': {
                    'name': TestData.resource_name,
                    'notes': TestData.resource_notes
                }
            }
            self.assertEqual(self.resource.update(parent=self.parent_resource), TestData.resource_from_data)
            self.mock_connection.patch.assert_called_once_with(expected_path, payload=expected_payload)

    def test_update_with_parent_error(self):
        self.parent_resource.id = None
        self.resource.id = TestData.resource_id
        with self.assertRaises(itglue.Configuration.ResourceError):
            self.resource.update(parent=self.parent_resource)

    def test_reload(self):
        self.assertEqual(self.resource._reload(TestData.data_dict), self.resource)
        self.assertEqual(self.resource.id, TestData.resource_id)
        self.assertEqual(self.resource.resource_type(), TestData.resource_type)
        self.assertEqual(self.resource.get_attr('name'), TestData.resource_alt_name)

    def test_payload(self):
        self.resource.id = TestData.resource_id
        expected_payload = {
            'id': TestData.resource_id,
            'type': TestData.resource_type,
            'attributes': {
                'name': TestData.resource_name,
                'notes': TestData.resource_notes
            }
        }
        self.assertEqual(self.resource.payload(), expected_payload)

    def test_relationships_payload(self):
        interface_1 = itglue.ConfigurationInterface(name='eni-545f123a', ip_address='1.2.3.4')
        interface_2 = itglue.ConfigurationInterface(name='eni-545f789a', ip_address='5.6.7.8')
        expected_rel_payload = {
            'configuration_interfaces': [
                {
                    'type': 'configuration_interfaces',
                    'attributes': {'name': 'eni-545f123a', 'ip_address': '1.2.3.4'}
                },
                {
                    'type': 'configuration_interfaces',
                    'attributes': {'name': 'eni-545f789a', 'ip_address': '5.6.7.8'}
                }
            ]
        }
        rel_payload = self.resource_class._relationships_payload({'configuration_interfaces': [interface_1, interface_2]})
        self.assertEqual(rel_payload, expected_rel_payload)

    def test_get(self):
        with patch.object(itglue.resources.connection, 'get', return_value=TestData.data_list):
            expected_path = '/{}'.format(TestData.resource_type)
            self.assertEqual(self.resource_class.get(), [TestData.resource_from_data])
            self.mock_connection.get.assert_called_once_with(expected_path)

    def test_get_with_parent(self):
        with patch.object(itglue.resources.connection, 'get', return_value=TestData.data_list):
            self.parent_resource.id = 456
            expected_path = '/{parent_type}/{parent_id}/relationships/{resource_type}'.format(
                parent_type=self.parent_resource.resource_type(),
                parent_id=self.parent_resource.id,
                resource_type=TestData.resource_type
            )
            resources = self.resource_class.get(parent=self.parent_resource)
            self.assertEqual(resources, [TestData.resource_from_data])
            self.mock_connection.get.assert_called_once_with(expected_path)

    def test_filter(self):
        with patch.object(itglue.resources.connection, 'get', return_value=TestData.data_list):
            expected_path = '/{}'.format(TestData.resource_type)
            expected_params = {'filter': {'name': TestData.resource_name}}
            resources = self.resource_class.filter(name=TestData.resource_name)
            self.assertEqual(resources, [TestData.resource_from_data])
            self.mock_connection.get.assert_called_once_with(expected_path, params=expected_params)

    def test_filter_no_filter_error(self):
        with self.assertRaises(itglue.Configuration.ResourceError):
            self.resource_class.filter(TestData.resource_type)

    def test_filter_all_nones_error(self):
        with self.assertRaises(itglue.Configuration.ResourceError):
            self.resource_class.filter(TestData.resource_type, name=None, notes='')

    def test_find(self):
        with patch.object(itglue.resources.connection, 'get', return_value=TestData.data_dict):
            expected_path = '/{}/{}'.format(TestData.resource_type, TestData.resource_id)
            resource = self.resource_class.find(TestData.resource_id)
            self.assertEqual(resource, TestData.resource_from_data)
            self.mock_connection.get.assert_called_once_with(expected_path)

    def test_find_with_parent(self):
        with patch.object(itglue.resources.connection, 'get', return_value=TestData.data_dict):
            self.parent_resource.id = 456
            expected_path = '/{parent_type}/{parent_id}/relationships/{resource_type}/{resource_id}'.format(
                parent_type=self.parent_resource.resource_type(),
                parent_id=self.parent_resource.id,
                resource_type=TestData.resource_type,
                resource_id=TestData.resource_id
            )
            resource = self.resource_class.find(TestData.resource_id, parent=self.parent_resource)
            self.assertEqual(resource, TestData.resource_from_data)
            self.mock_connection.get.assert_called_once_with(expected_path)

    def test_first_or_create_with_match(self):
        with patch.object(itglue.resources.connection, 'get', return_value=TestData.data_list):
            expected_path = '/{}'.format(TestData.resource_type)
            expected_params = {'filter': {'name': TestData.resource_name}}
            resource = self.resource_class.first_or_create(name=TestData.resource_name)
            self.assertEqual(resource, TestData.resource_from_data)
            self.mock_connection.get.assert_called_once_with(expected_path, params=expected_params)
            self.mock_connection.post.assert_not_called()

    def test_first_or_create_without_match(self):
        with patch.object(itglue.resources.connection, 'get', return_value=[]), \
                patch.object(itglue.resources.connection, 'post', return_value=TestData.data_dict):
            expected_path = '/{}'.format(TestData.resource_type)
            expected_params = {'filter': {'name': TestData.resource_name}}
            expected_payload = {
                'type': TestData.resource_type,
                'attributes': {
                    'name': TestData.resource_name
                }
            }
            resource = self.resource_class.first_or_create(name=TestData.resource_name)
            self.assertEqual(resource, TestData.resource_from_data)
            self.mock_connection.get.assert_called_once_with(expected_path, params=expected_params)
            self.mock_connection.post.assert_called_once_with(expected_path, payload=expected_payload, relationships={})

    def test_first_or_initialize_with_match(self):
        with patch.object(itglue.resources.connection, 'get', return_value=TestData.data_list):
            expected_path = '/{}'.format(TestData.resource_type)
            expected_params = {'filter': {'name': TestData.resource_name}}
            resource = self.resource_class.first_or_initialize(name=TestData.resource_name)
            self.assertEqual(resource, TestData.resource_from_data)
            self.mock_connection.get.assert_called_once_with(expected_path, params=expected_params)
            self.mock_connection.post.assert_not_called()

    def test_first_or_initialize_without_match(self):
        with patch.object(itglue.resources.connection, 'get', return_value=[]):
            expected_path = '/{}'.format(TestData.resource_type)
            expected_params = {'filter': {'name': TestData.resource_name}}
            resource = self.resource_class.first_or_initialize(name=TestData.resource_name)
            self.assertEqual(resource, itglue.Configuration(name=TestData.resource_name))
            self.mock_connection.get.assert_called_once_with(expected_path, params=expected_params)
            self.mock_connection.post.assert_not_called()

    def test_find_by(self):
        with patch.object(itglue.resources.connection, 'get', return_value=TestData.data_list):
            expected_path = '/{}'.format(TestData.resource_type)
            expected_params = {'filter': {'name': TestData.resource_name}}
            resource = self.resource_class.find_by(name=TestData.resource_name)
            self.assertEqual(resource, TestData.resource_from_data)
            self.mock_connection.get.assert_called_once_with(expected_path, params=expected_params)

    def test_find_by_no_matches(self):
        with patch.object(itglue.resources.connection, 'get', return_value=[]):
            expected_path = '/{}'.format(TestData.resource_type)
            expected_params = {'filter': {'name': TestData.resource_name}}
            resource = self.resource_class.find_by(name=TestData.resource_name)
            self.assertEqual(resource, None)
            self.mock_connection.get.assert_called_once_with(expected_path, params=expected_params)

    def test_find_by_no_attributes_error(self):
        with self.assertRaises(itglue.Configuration.ResourceError):
            self.resource_class.find_by()

    def test_find_by_all_empty_error(self):
        with self.assertRaises(itglue.Configuration.ResourceError):
            self.resource_class.find_by(name=None, notes='')


if __name__ == '__main__':
    unittest.main()
