import { defineStore } from 'pinia'
import { deviceApi } from '../services/deviceApi'

export const useDeviceStore = defineStore('devices', {
  state: () => ({
    usbScan: [] as Array<Record<string, string>>,
    usbParser: [] as Array<Record<string, string>>,
    ports: [] as string[],
    dependencies: [] as Array<Record<string, string>>,
    toolchains: [] as string[],
    toolchainStates: [] as Array<Record<string, string>>,
    environmentPaths: {} as Record<string, string>,
  }),
  actions: {
    async fetchDevices() {
      const data = await deviceApi.list()
      this.usbScan = data.usb_scan
      this.usbParser = data.usb_parser
      this.ports = data.ports
    },
    async fetchEnvironment() {
      const [deps, chains, detect, env] = await Promise.all([
        deviceApi.dependencies(),
        deviceApi.toolchains(),
        deviceApi.toolchainsDetect(),
        deviceApi.environment(),
      ])
      this.dependencies = deps.items
      this.toolchains = chains.items
      this.toolchainStates = detect.items
      this.environmentPaths = env.paths
    },
  },
})
