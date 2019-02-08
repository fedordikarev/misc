#!/usr/bin/env python3

from googleapiclient.discovery import build
import json

class google_compute_api:
    predef_mach_types = dict()
    all_disks = dict()

    api_connection = None

    def __init__(self, project='default_project', zone='default_zone'):
        self.project = project
        self.zone = zone

        self.api_connection = build('compute', 'v1')

    def get_mach_type(self, url):
        name = url.split('/')[-1]

        if name.startswith('custom-'):
            _, guestCpus, memoryMb = name.split('-')
            return { 'guestCpus': int(guestCpus), 'memoryMb': int(memoryMb) }

        if not self.predef_mach_types:
            self.init_mach_types()

        if name in self.predef_mach_types:
            return self.predef_mach_types[name]

        raise ValueError("unknown mach type "+name)

    def init_mach_types(self):
        mach_types_list = self.api_connection.machineTypes().list(
                project=self.project, zone=self.zone,
                fields='items/name,items/guestCpus,items/memoryMb').execute()

        for item in mach_types_list['items']:
            self.predef_mach_types[item['name']] = {'guestCpus': item['guestCpus'], 'memoryMb': item['memoryMb']}

    def get_all_disks(self):
        all_disks_list = self.api_connection.disks().list(
                project=self.project, zone=self.zone,
                fields='items/name,items/sizeGb').execute()

        for item in all_disks_list['items']:
            self.all_disks[item['name']] = { 'sizeGb': int(item['sizeGb']) }

    def get_disk_info(self, url):
        name = url.split('/')[-1]

        if not self.all_disks:
            self.get_all_disks()

        return self.all_disks.get(name, { 'sizeGb': 'not_found' })

    def list_instances(self):
        instances_list = self.api_connection.instances().list(
                project=self.project, zone=self.zone,
                fields='items/name,items/machineType,items/disks').execute()

        result = dict()
        for item in instances_list['items']:
            result[item['name']] = self.get_mach_type(item['machineType'])
            # print(item['name'], self.get_mach_type(item['machineType']))
            total_disk_size = 0
            for disk in item['disks']:
                total_disk_size += self.get_disk_info(disk['deviceName'])['sizeGb']
                # print(self.get_disk_info(disk['deviceName']))
            result[item['name']]['totalDiskGb'] = total_disk_size

        print(json.dumps(result))
        # print(result)

        print("{:<12} {:<15} {:<10} {:<10}".format('Name','Cpu','MemoryGb','Disk'))
        for k, v in result.items():
            print("{:<12} {:<15} {:<10} {:<10}".format(k, v['guestCpus'], (v['memoryMb']/1024), v['totalDiskGb']))

def main():
    api = google_compute_api()
    api.list_instances()

if __name__ == "__main__":
    main()
