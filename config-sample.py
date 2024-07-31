import platform

idrive = {
  'endpoint' : "https://n4v6.da.idrivee2-31.com",
  'bucket' : "slt",
  'accessKeyId' : "<your access key>",
  'secretAccessKey' : "<your secret key>"
}

weatherkit = {
  'token' : "<your weatherkit token>"
}

telescopes = {
  'slt' : {
    'shortname' : 'slt',
    'fullname' : 'sufficiently large Telescope',
    'location' : 'Starfront Observatory',
    'schedulerdb' : "c:/Users/ring/AppData/Local/NINA/SchedulerPlugin/schedulerdb.sqlite",
    'nodename' : "nina-lacerta"
  },
  'vst' : {
    'shortname' : 'vst',
    'fullname' : 'very small Telescope',
    'location': 'Starfront Observatory',
    'schedulerdb': "c:/Users/mail/AppData/Local/NINA/SchedulerPlugin/schedulerdb.sqlite",
    'nodename': "nina-askar"
  },
  'edgehd925': {
    'shortname' : 'edgehd925',
    'fullname': 'Fat Boy',
    'location': 'Gantrisch',
    'schedulerdb': "c:/Users/ring/AppData/Local/NINA/SchedulerPlugin/schedulerdb.sqlite",
    'nodename': "nina-edgehd"
  },
  'cdk14': {
    'shortname' : 'cdk14',
    'fullname': 'Moana reloaded',
    'location': 'Prairie Skies Astro Ranch',
    'schedulerdb': "c:/Users/guill/AppData/Local/NINA/SchedulerPlugin/schedulerdb.sqlite",
    'nodename': 'nina-unknown',
  },
  'testing': {
    'shortname': 'slt',
    'fullname': 'SLT Telescope Test',
    'location': 'Gantrisch',
    'schedulerdb': "/Users/tgdrimi9/devel/slt-observatoryMonitoring/schedulerdb.sqlite",
    'nodename': "macbookpro14.home"
  },
}

locations = {
  'Gantrisch' : {
    'latitude': "46.73196228867647",
    'longitude': "7.446461671486496",
    'country': "CH",
    'timezone': ("CH/Zurich"),
    'language': "en",
    'elevation': 1650,
    'locationcode': "gantrisch"
  },
  'Starfront Observatory' : {
    'latitude': "31.547485160577963",
    'longitude': "-99.38248464510205",
    'country': "US",
    'timezone': ("US/Central"),
    'language': "en",
    'elevation': 850,
    'locationcode': "starfront"
  },
  'Prairie Skies Astro Ranch': {
    'latitude': "31.57472",
    'longitude': "-96.44027",
    'country': "US",
    'timezone': ("US/Central"),
    'language': "en",
    'elevation': 173,
    'locationcode': "cdk14"
  }
}

nodeName = platform.uname().node
telescope = telescopes['testing']
for _telescope in telescopes:
  if telescopes[_telescope]['nodename'] == nodeName:
    telescope = telescopes[_telescope]
    break
