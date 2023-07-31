#
# (c) 2022, Ansible by Red Hat, inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#

from __future__ import absolute_import, division, print_function


__metaclass__ = type

from textwrap import dedent

from ansible_collections.cisco.ios.plugins.modules import ios_interfaces
from ansible_collections.cisco.ios.tests.unit.compat.mock import patch
from ansible_collections.cisco.ios.tests.unit.modules.utils import set_module_args

from .ios_module import TestIosModule


class TestIosInterfacesModule(TestIosModule):
    module = ios_interfaces

    def setUp(self):
        super(TestIosInterfacesModule, self).setUp()

        self.mock_get_config = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.network.Config.get_config",
        )
        self.get_config = self.mock_get_config.start()

        self.mock_load_config = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.network.Config.load_config",
        )
        self.load_config = self.mock_load_config.start()

        self.mock_get_resource_connection_config = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.cfg.base."
            "get_resource_connection",
        )
        self.get_resource_connection_config = self.mock_get_resource_connection_config.start()

        self.mock_get_resource_connection_facts = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base."
            "get_resource_connection",
        )
        self.get_resource_connection_facts = self.mock_get_resource_connection_facts.start()

        self.mock_edit_config = patch(
            "ansible_collections.cisco.ios.plugins.module_utils.network.ios.providers.providers.CliProvider.edit_config",
        )
        self.edit_config = self.mock_edit_config.start()

        self.mock_execute_show_command = patch(
            "ansible_collections.cisco.ios.plugins.module_utils.network.ios.facts.interfaces.interfaces."
            "InterfacesFacts.get_interfaces_data",
        )
        self.execute_show_command = self.mock_execute_show_command.start()

    def tearDown(self):
        super(TestIosInterfacesModule, self).tearDown()
        self.mock_get_resource_connection_config.stop()
        self.mock_get_resource_connection_facts.stop()
        self.mock_edit_config.stop()
        self.mock_get_config.stop()
        self.mock_load_config.stop()
        self.mock_execute_show_command.stop()

    def test_ios_interfaces_merged(self):
        self.execute_show_command.return_value = dedent(
            """\
            interface GigabitEthernet1
             description Ansible UT interface 1
             no shutdown
             ip address dhcp
             negotiation auto
            interface GigabitEthernet0/1
             description Ansible UT interface 2
             ip address dhcp
             speed 1000
             mtu 1500
             no negotiation auto
            interface GigabitEthernet3
             description Ansible UT interface 3
             no ip address
             shutdown
             duplex auto
             negotiation auto
             channel-group 10 mode active
            interface GigabitEthernet4
             description Ansible UT interface 4
             no ip address
             shutdown
             negotiation auto
            interface GigabitEthernet5
             description Ansible UT interface 5
             no ip address
             duplex full
             negotiation auto
             ipv6 dhcp server
            interface GigabitEthernet6
             description Ansible UT interface 6
            """,
        )
        set_module_args(
            {
                "config": [
                    {
                        "description": "This interface should be disabled",
                        "enabled": True,
                        "name": "GigabitEthernet1",
                    },
                    {
                        "description": "This interface should be enabled",
                        "enabled": False,
                        "name": "GigabitEthernet0/1",
                    },
                    {"mode": "layer3", "name": "GigabitEthernet6"},
                ],
                "state": "merged",
            },
        )
        commands = [
            "interface GigabitEthernet0/1",
            "description This interface should be enabled",
            "shutdown",
            "interface GigabitEthernet1",
            "description This interface should be disabled",
            "interface GigabitEthernet6",
            "no switchport",
        ]
        result = self.execute_module(changed=True)
        self.assertEqual(result["commands"], commands)

    def test_ios_interfaces_merged_idempotent(self):
        self.execute_show_command.return_value = dedent(
            """\
            interface GigabitEthernet1
             description Ansible UT interface 1
             no shutdown
             ip address dhcp
             negotiation auto
            interface GigabitEthernet0/1
             description Ansible UT interface 2
             ip address dhcp
             speed 1000
             mtu 1500
             no negotiation auto
            interface GigabitEthernet3
             description Ansible UT interface 3
             no ip address
             shutdown
             duplex auto
             negotiation auto
             channel-group 10 mode active
            interface GigabitEthernet4
             description Ansible UT interface 4
             no ip address
             shutdown
             negotiation auto
            interface GigabitEthernet5
             description Ansible UT interface 5
             no ip address
             duplex full
             negotiation auto
             ipv6 dhcp server
            """,
        )
        set_module_args(
            {
                "config": [
                    {"description": "Ansible UT interface 1", "name": "GigabitEthernet1"},
                    {
                        "description": "Ansible UT interface 2",
                        "name": "GigabitEthernet0/1",
                        "speed": 1000,
                        "mtu": 1500,
                    },
                ],
                "state": "merged",
            },
        )
        self.execute_module(changed=False, commands=[])

    def test_ios_interfaces_replaced(self):
        self.execute_show_command.return_value = dedent(
            """\
            interface GigabitEthernet1
             description Ansible UT interface 1
             no shutdown
             ip address dhcp
             negotiation auto
            interface GigabitEthernet0/1
             description Ansible UT interface 2
             ip address dhcp
             speed 1000
             mtu 1500
             no negotiation auto
            interface GigabitEthernet3
             description Ansible UT interface 3
             no ip address
             shutdown
             duplex auto
             negotiation auto
             channel-group 10 mode active
            interface GigabitEthernet4
             description Ansible UT interface 4
             no ip address
             shutdown
             negotiation auto
            interface GigabitEthernet5
             description Ansible UT interface 5
             no ip address
             duplex full
             negotiation auto
             ipv6 dhcp server
            interface GigabitEthernet6
             description Ansible UT interface 6
             no switchport
            """,
        )
        set_module_args(
            {
                "config": [
                    {"description": "Ansible UT interface 1", "name": "GigabitEthernet1"},
                    {"name": "GigabitEthernet0/1", "speed": 1200, "mtu": 1800},
                    {
                        "name": "GigabitEthernet6",
                        "description": "Ansible UT interface 6",
                        "mode": "layer2",
                    },
                ],
                "state": "replaced",
            },
        )
        commands = [
            "interface GigabitEthernet0/1",
            "no description Ansible UT interface 2",
            "speed 1200",
            "mtu 1800",
            "interface GigabitEthernet6",
            "switchport",
        ]
        result = self.execute_module(changed=True)
        self.assertEqual(result["commands"], commands)

    def test_ios_interfaces_replaced_idempotent(self):
        self.execute_show_command.return_value = dedent(
            """\
            interface GigabitEthernet1
             description Ansible UT interface 1
             no shutdown
             ip address dhcp
             negotiation auto
            interface GigabitEthernet0/1
             description Ansible UT interface 2
             ip address dhcp
             speed 1000
             mtu 1500
             no negotiation auto
            interface GigabitEthernet3
             description Ansible UT interface 3
             no ip address
             shutdown
             duplex auto
             negotiation auto
             channel-group 10 mode active
            interface GigabitEthernet4
             description Ansible UT interface 4
             no ip address
             shutdown
             negotiation auto
            interface GigabitEthernet5
             description Ansible UT interface 5
             no ip address
             duplex full
             negotiation auto
             ipv6 dhcp server
            """,
        )
        set_module_args(
            {
                "config": [
                    {"description": "Ansible UT interface 1", "name": "GigabitEthernet1"},
                    {
                        "description": "Ansible UT interface 2",
                        "name": "GigabitEthernet0/1",
                        "speed": 1000,
                        "mtu": 1500,
                    },
                ],
                "state": "replaced",
            },
        )
        self.execute_module(changed=False, commands=[])

    def test_ios_interfaces_overridden(self):
        self.execute_show_command.return_value = dedent(
            """\
            interface GigabitEthernet1
             description Ansible UT interface 1
             no shutdown
             ip address dhcp
             negotiation auto
            interface GigabitEthernet0/1
             description Ansible UT interface 2
             ip address dhcp
             speed 1000
             mtu 1500
             no negotiation auto
            interface GigabitEthernet3
             description Ansible UT interface 3
             no ip address
             shutdown
             duplex auto
             negotiation auto
             channel-group 10 mode active
            interface GigabitEthernet4
             description Ansible UT interface 4
             no ip address
             shutdown
             negotiation auto
            interface GigabitEthernet5
             description Ansible UT interface 5
             no ip address
             duplex full
             negotiation auto
             ipv6 dhcp server
            interface GigabitEthernet6
             description Ansible UT interface 6
             no switchport
            """,
        )
        set_module_args(
            {
                "config": [
                    {
                        "description": "Ansible UT interface try 1",
                        "speed": 1000,
                        "name": "GigabitEthernet1",
                    },
                    {
                        "description": "Ansible UT interface 2",
                        "name": "GigabitEthernet3",
                        "speed": 1000,
                        "mtu": 1500,
                    },
                ],
                "state": "overridden",
            },
        )

        commands = [
            "interface GigabitEthernet0/1",
            "no description Ansible UT interface 2",
            "no speed 1000",
            "no mtu 1500",
            "shutdown",
            "interface GigabitEthernet4",
            "no description Ansible UT interface 4",
            "interface GigabitEthernet5",
            "no description Ansible UT interface 5",
            "no duplex full",
            "shutdown",
            "interface GigabitEthernet6",
            "no description Ansible UT interface 6",
            "shutdown",
            "switchport",
            "interface GigabitEthernet1",
            "description Ansible UT interface try 1",
            "speed 1000",
            "interface GigabitEthernet3",
            "description Ansible UT interface 2",
            "speed 1000",
            "mtu 1500",
            "no duplex auto",
            "no shutdown",
        ]
        result = self.execute_module(changed=True)
        self.assertEqual(result["commands"], commands)

    def test_ios_interfaces_deleted(self):
        self.execute_show_command.return_value = dedent(
            """\
            interface GigabitEthernet1
             description Ansible UT interface 1
             no shutdown
             ip address dhcp
             negotiation auto
            interface GigabitEthernet0/1
             description Ansible UT interface 2
             ip address dhcp
             speed 1000
             mtu 1500
             no negotiation auto
            interface GigabitEthernet3
             description Ansible UT interface 3
             no ip address
             shutdown
             duplex auto
             negotiation auto
             channel-group 10 mode active
            interface GigabitEthernet4
             description Ansible UT interface 4
             no ip address
             shutdown
             negotiation auto
            interface GigabitEthernet5
             description Ansible UT interface 5
             no ip address
             duplex full
             negotiation auto
             ipv6 dhcp server
            """,
        )
        set_module_args(dict(config=[dict(name="GigabitEthernet1")], state="deleted"))
        commands = [
            "interface GigabitEthernet1",
            "no description Ansible UT interface 1",
            "shutdown",
        ]
        result = self.execute_module(changed=True)
        self.assertEqual(result["commands"], commands)

    def test_ios_interfaces_purged(self):
        self.execute_show_command.return_value = dedent(
            """\
            interface GigabitEthernet1
             description Ansible UT interface 1
             no shutdown
             ip address dhcp
             negotiation auto
            interface GigabitEthernet0/1
             description Ansible UT interface 2
             ip address dhcp
             speed 1000
             mtu 1500
             no negotiation auto
            interface GigabitEthernet3
             description Ansible UT interface 3
             no ip address
             shutdown
             duplex auto
             negotiation auto
             channel-group 10 mode active
            interface GigabitEthernet4
             description Ansible UT interface 4
             no ip address
             shutdown
             negotiation auto
            interface GigabitEthernet5
             description Ansible UT interface 5
             no ip address
             duplex full
             negotiation auto
             ipv6 dhcp server
            """,
        )
        set_module_args(
            dict(
                config=[
                    {
                        "name": "GigabitEthernet0/1",
                        "description": "Ansible UT interface 2",
                        "speed": "1000",
                        "mtu": 1500,
                        "enabled": True,
                    },
                    {
                        "name": "GigabitEthernet3",
                        "description": "Ansible UT interface 3",
                        "enabled": True,
                        "duplex": "auto",
                    },
                ],
                state="purged",
            ),
        )
        commands = ["no interface GigabitEthernet0/1", "no interface GigabitEthernet3"]
        result = self.execute_module(changed=True)
        self.assertEqual(result["commands"], commands)

    def test_ios_interfaces_purged_extreme(self):
        self.execute_show_command.return_value = dedent(
            """\
            interface GigabitEthernet1
             description Ansible UT interface 1
             no shutdown
             ip address dhcp
             negotiation auto
            interface GigabitEthernet0/1
             description Ansible UT interface 2
             ip address dhcp
             speed 1000
             mtu 1500
             no negotiation auto
            interface GigabitEthernet3
             description Ansible UT interface 3
             no ip address
             shutdown
             duplex auto
             negotiation auto
             channel-group 10 mode active
            interface GigabitEthernet4
             description Ansible UT interface 4
             no ip address
             shutdown
             negotiation auto
            interface GigabitEthernet5
             description Ansible UT interface 5
             no ip address
             duplex full
             negotiation auto
             ipv6 dhcp server
            """,
        )
        set_module_args(dict(config=[], state="purged"))
        commands = [
            "no interface GigabitEthernet0/1",
            "no interface GigabitEthernet1",
            "no interface GigabitEthernet3",
            "no interface GigabitEthernet4",
            "no interface GigabitEthernet5",
        ]
        result = self.execute_module(changed=True)
        self.assertEqual(result["commands"], commands)

    def test_ios_interfaces_parsed(self):
        set_module_args(
            dict(
                running_config=dedent(
                    """\
                    interface GigabitEthernet1
                     description Ansible UT interface 1
                     no shutdown
                     ip address dhcp
                     negotiation auto
                    interface GigabitEthernet0/1
                     description Ansible UT interface 2
                     ip address dhcp
                     speed 1000
                     mtu 1500
                     no negotiation auto
                    interface GigabitEthernet3
                     description Ansible UT interface 3
                     no ip address
                     shutdown
                     duplex auto
                     negotiation auto
                     channel-group 10 mode active
                    interface GigabitEthernet4
                     description Ansible UT interface 4
                     no ip address
                     shutdown
                     negotiation auto
                    interface GigabitEthernet5
                     description Ansible UT interface 5
                     no ip address
                     duplex full
                     negotiation auto
                     ipv6 dhcp server
                    interface GigabitEthernet6
                     description Ansible UT interface 6
                     switchport
                    interface GigabitEthernet7
                     description Ansible UT interface 7
                     no switchport
                    """,
                ),
                state="parsed",
            ),
        )
        result = self.execute_module(changed=False)
        parsed_list = [
            {
                "name": "GigabitEthernet0/1",
                "description": "Ansible UT interface 2",
                "speed": "1000",
                "mtu": 1500,
                "enabled": True,
            },
            {"name": "GigabitEthernet1", "description": "Ansible UT interface 1", "enabled": True},
            {
                "name": "GigabitEthernet3",
                "description": "Ansible UT interface 3",
                "enabled": False,
                "duplex": "auto",
            },
            {"name": "GigabitEthernet4", "description": "Ansible UT interface 4", "enabled": False},
            {
                "name": "GigabitEthernet5",
                "description": "Ansible UT interface 5",
                "duplex": "full",
                "enabled": True,
            },
            {
                "name": "GigabitEthernet6",
                "mode": "layer2",
                "description": "Ansible UT interface 6",
                "enabled": True,
            },
            {
                "name": "GigabitEthernet7",
                "mode": "layer3",
                "description": "Ansible UT interface 7",
                "enabled": True,
            },
        ]
        self.assertEqual(parsed_list, result["parsed"])

    def test_ios_interfaces_rendered(self):
        self.execute_show_command.return_value = dedent(
            """\
            interface GigabitEthernet1
             description Ansible UT interface 1
            interface GigabitEthernet0/1
             description Ansible UT interface 2
             ip address dhcp
            interface GigabitEthernet3
             no ip address
            interface GigabitEthernet4
             negotiation auto
            interface GigabitEthernet5
             ipv6 dhcp server
            """,
        )
        set_module_args(
            dict(
                config=[
                    {
                        "name": "GigabitEthernet1",
                        "description": "Ansible UT interface 1",
                        "enabled": False,
                    },
                    {
                        "name": "GigabitEthernet0/1",
                        "description": "Ansible UT interface 2",
                        "speed": "1000",
                        "mtu": 1500,
                        "enabled": True,
                    },
                    {
                        "name": "GigabitEthernet3",
                        "description": "Ansible UT interface 3",
                        "enabled": True,
                        "duplex": "auto",
                    },
                    {
                        "name": "GigabitEthernet4",
                        "description": "Ansible UT interface 4",
                        "enabled": True,
                    },
                    {
                        "name": "GigabitEthernet5",
                        "description": "Ansible UT interface 5",
                        "duplex": "full",
                        "enabled": True,
                    },
                ],
                state="rendered",
            ),
        )

        commands = [
            "interface GigabitEthernet1",
            "description Ansible UT interface 1",
            "shutdown",
            "interface GigabitEthernet0/1",
            "description Ansible UT interface 2",
            "speed 1000",
            "mtu 1500",
            "no shutdown",
            "interface GigabitEthernet3",
            "description Ansible UT interface 3",
            "duplex auto",
            "no shutdown",
            "interface GigabitEthernet4",
            "description Ansible UT interface 4",
            "no shutdown",
            "interface GigabitEthernet5",
            "description Ansible UT interface 5",
            "duplex full",
            "no shutdown",
        ]
        result = self.execute_module(changed=False)
        self.assertEqual(sorted(result["rendered"]), sorted(commands))
