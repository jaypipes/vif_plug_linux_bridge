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

from os_vif import plugin
from os_vif import objects

from vif_plug_linux_bridge import processutils
from vif_plug_linux_bridge import linux_net

PLUGIN_NAME = 'bridge'


class LinuxBridgePlugin(plugin.PluginBase):
    """A VIF type that uses a standard Linux bridge device."""
    
    def __init__(self, **config):
        processutils.configure(**config)
        linux_net.configure(**config)
        self.network_device_mtu = config.get('network_device_mtu', 1500)
        self.vlan_interface = config.get('vlan_interface')
        self.flat_interface = config.get('flat_interface')

    def get_supported_vifs(self):
        return set([objects.PluginVIFSupport(PLUGIN_NAME, '1.0', '1.0')])

    def plug(self, instance, vif):
        """Ensure that the bridge exists, and add VIF to it."""
        network = vif.network
        bridge_name = vif.bridge_name
        if not network.multi_host and network.should_create_bridge:
            if network.should_create_vlan:
                iface = self.vlan_interface or network.bridge_interface
                mtu = self.network_device_mtu
                linux_net.ensure_vlan_bridge(network.vlan,
                                             bridge_name, iface, mtu=mtu)
            else:
                iface = self.flat_interface or network.bridge_interface
                linux_net.ensure_bridge(bridge_name, iface)

    def unplug(self, vif):
        # Nothing required to unplug a port for a VIF using standard
        # Linux bridge device...
        pass
