security_group_response = '''{
  "metadata": {
    "guid": "1452e164-0c3e-4a6c-b3c3-c40ad9fd0159",
    "url": "/v2/security_groups/1452e164-0c3e-4a6c-b3c3-c40ad9fd0159",
    "created_at": "2016-06-08T16:41:21Z",
    "updated_at": "2016-06-08T16:41:26Z"
  },
  "entity": {
    "name": "dummy1",
    "rules": [
          {
            "protocol": "udp",
            "ports": "8080",
            "destination": "198.41.191.47/1"
          }
    ],
    "running_default": false,
    "staging_default": false,
    "spaces_url": "/v2/security_groups/1452e164-0c3e-4a6c-b3c3-c40ad9fd0159/spaces",
    "staging_spaces_url": "/v2/security_groups/1452e164-0c3e-4a6c-b3c3-c40ad9fd0159/staging_spaces"
  }
}'''