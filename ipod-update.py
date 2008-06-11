#!/usr/bin/python
import plistlib
import StringIO
import commands
import dbus
import gzip
import shutil
import urlgrabber
import urlgrabber.progress
import xml.sax
import zipfile

class IPodUpdate (object):
	def findPods(self):
		results = []
		bus = dbus.SystemBus()
		try:
			hal_manager_obj = bus.get_object('org.freedesktop.Hal',
				'/org/freedesktop/Hal/Manager')
			hal_manager = dbus.Interface(hal_manager_obj,
				'org.freedesktop.Hal.Manager')
			dev_udi_list = hal_manager.FindDeviceStringMatch ('storage.model', 'iPod')
			for udi in dev_udi_list:
				vol_udi_list = hal_manager.FindDeviceStringMatch ('info.parent', udi)
				label = '(unknown)'
				device = None
				for vol_udi in vol_udi_list:
					vol_obj = bus.get_object ('org.freedesktop.Hal', vol_udi)
					vol = dbus.Interface (vol_obj, 'org.freedesktop.Hal.Device')

					if vol.GetProperty('volume.partition.type') == '0x00':
						device = vol.GetProperty('block.device')
					elif vol.GetProperty('volume.is_mounted'):
						label = vol.GetProperty('volume.label')
				# FIXME: improve podsleuth to report family ID for a pure Hal solution
				if (device):
					results.append((device, label, None, None))
				break
		except:
			print 'HAL is down?'

		return results

	def getIPodData(self, dev):
		# FIXME: any idea how to get it done in pure python?
		offsets = commands.getoutput('sg_inq "%s" --page=192 --raw --vpd' % dev)[4:]
		data = ''
		for offset in offsets:
			data += commands.getoutput('sg_inq "%s" --page=%d --raw --vpd' % (dev, ord(offset)))[4:]
		print data
		parsed = plistlib.readPlistFromString(data)
		family = parsed['UpdaterFamilyID']
		firmware = parsed['VisibleBuildID']
		return (family, firmware)

	def __init__(self):
		data = StringIO.StringIO(urlgrabber.urlread('http://itunes.com/version'))
		stream = gzip.GzipFile(fileobj = data)
		data = stream.read()
		updates = plistlib.readPlistFromString(data)
		devs = self.findPods()
		for (dev, name, family, firmware) in devs:
			if not family:
				family, firmware = self.getIPodData(dev)
			print 'Found %s with family %s and firmware %s' % (name, family, firmware)
			if updates['iPodSoftwareVersions'].has_key(unicode(family)):
				uri = updates['iPodSoftwareVersions'][unicode(family)]['FirmwareURL']
				print 'Latest firmware: %s' % uri
				print 'Fetching firmware...'
				path = urlgrabber.urlgrab(uri, progress_obj = urlgrabber.progress.text_progress_meter(), reget = 'check_timestamp')
				print 'Extracting firmware...'
				zf = zipfile.ZipFile(path)
				for name in zf.namelist():
					if name[:8] == 'Firmware':
						print 'Firmware found.'
						outfile = open('Firmware', 'wb')
						outfile.write(zf.read(name))
						outfile.close()
						infile = open('Firmware', 'rb')
						outfile = open(dev, 'wb')
						# FIXME: do the following in pure python?
						print 'Making backup...'
						commands.getoutput('dd if=%s of=Backup' % dev)
						print 'Uploading firmware...'
						commands.getoutput('dd if=Firmware of=%s' % dev)
			print 'Done.'

IPodUpdate()
