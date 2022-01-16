#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: digital_ocean_spaces_info
short_description: List DigitalOcean Spaces.
description:
  - List DigitalOcean Spaces.
author: Mark Mercado (@mamercad)
options:
  state:
    description:
     - Only present is supported.
    default: present
    type: str
    choices: ["present"]
  name:
    description:
      - The name of the Space to list.
    required: true
    type: str
  region:
    description:
      - The region from which to list Spaces.
    aliases: ["region_id"]
    required: true 
    type: str
  aws_access_key_id:
    description:
      - The AWS_ACCESS_KEY_ID to use.
    required: true
    type: str
    aliases: ["AWS_ACCESS_KEY_ID"]
  aws_secret_acccess_key:
    description:
      - The AWS_SECRET_ACCESS_KEY to use.
    required: true
    type: str
    aliases: ["AWS_SECRET_ACCESS_KEY"]
requirements:
  - boto3    
"""


EXAMPLES = r"""
- name: List all Spaces in nyc3
  community.digitalocean.digital_ocean_spaces_info:
    state: present
    region: nyc3
"""


RETURN = r"""
data:
  description: List of DigitalOcean Spaces
  returned: always
  type: dict
  sample: 
    spaces:
      - endpoint_url: https://nyc3.digitaloceanspaces.com
        name: gh-ci-space
        region: nyc3
        space_url: https://gh-ci-space.nyc3.digitaloceanspaces.com
"""

from ansible.module_utils.basic import AnsibleModule, missing_required_lib, env_fallback
from ansible_collections.community.digitalocean.plugins.module_utils.digital_ocean import (
    DigitalOceanHelper,
)

try:
    import boto3

    HAS_BOTO3 = True
except Exception:
    HAS_BOTO3 = False


def run(module):
    state = module.params.get("state")
    name = module.params.get("name")
    region = module.params.get("region")
    aws_access_key_id = module.params.get("aws_access_key_id")
    aws_secret_access_key = module.params.get("aws_secret_access_key")

    if state == "present":
        session = boto3.session.Session()
        client = session.client(
            "s3",
            region_name=region,
            endpoint_url=f"https://{region}.digitaloceanspaces.com",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        response = client.list_buckets()
        spaces = [
            {
                "name": space["Name"],
                "region": region,
                "endpoint_url": f"https://{region}.digitaloceanspaces.com",
                "space_url": f"https://{space['Name']}.{region}.digitaloceanspaces.com",
            }
            for space in response["Buckets"]
        ]
        module.exit_json(changed=False, data={"spaces": spaces})


def main():

    argument_spec = DigitalOceanHelper.digital_ocean_argument_spec()
    argument_spec.update(
        state=dict(choices=["present", "absent"], default="present"),
        name=dict(type="str", required=True),
        region=dict(type="str", aliases=["region_id"], required=True),
        aws_access_key_id=dict(
            type="str",
            aliases=["AWS_ACCESS_KEY_ID"],
            fallback=(env_fallback, ["AWS_ACCESS_KEY_ID"]),
            required=True,
        ),
        aws_secret_access_key=dict(
            type="str",
            aliases=["AWS_SECRET_ACCESS_KEY"],
            fallback=(env_fallback, ["AWS_SECRET_ACCESS_KEY"]),
            required=True,
        ),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    if not HAS_BOTO3:
        module.fail_json(msg=missing_required_lib("boto3"))

    run(module)


if __name__ == "__main__":
    main()
