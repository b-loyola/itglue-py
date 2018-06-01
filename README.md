# IT Glue

A Simple python wrapper for the [IT Glue API](https://api.itglue.com/developer/).

## Installation

```python
pip install itglue
```

## Requirements

* Python 3.6 or higher

## Setup

### Authentication

For now this gem only supports API Key authentication.

### Configuration

```python
import itglue

itglue.connection.api_url = 'https://api.itglue.com'
itglue.connection.api_key = 'YOUR_API_KEY'
```

## Usage

### Basics

Get all organizations
```python
>>> itglue.Organization.get()
[<Organization id: 123, attributes: {...}>, <Organization id: 456, attributes: {...}>, ...]
```
Get organizations with a filter
```python
>>> itglue.Organization.filter(name='Happy Frog')
[<Organization id: 123, attributes: {'name': 'Happy Frog', ...}>, ...]
```
Get organization by id
```python
>>> itglue.Organization.find(123)
<Organization id: 123, attributes: {...}>
```
Get configurations for a specific organization
```python
>>> organization = itglue.Organization.find(123)
>>> itglue.Configuration.get(parent=organization)
[<Configuration id: 456, attributes: {...}>, <Configuration id: 789, attributes: {...}>, ...]
```

### Client

You can also use the connection to execute requests and handle the data and response directly.
```python
>>> itglue.connection.get('/configurations', params={ 'filter': {'name': 'HP-1'} })
[{'attributes': {'name': 'HP-1', 'id': '123', ...}, 'relationships': {} }, ...]
```

## Contributing

Bug reports and pull requests are welcome on GitHub at https://github.com/b-loyola/itglue-py.

## License

The gem is available as open source under the terms of the [MIT License](https://opensource.org/licenses/MIT).
