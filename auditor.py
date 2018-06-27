# coding:utf-8
import os
import argparse
import requests
import logging

from google.cloud import vision
from google.cloud.vision import types

logging.basicConfig(level=logging.INFO, format='%(message)s')

SLACK_URL = 'https://{slack}.slack.com/api/emoji.list?token={token}'
RESPONSE_TYPE = ('adult', 'spoof', 'medical', 'violence', 'racy')
LIKEHOOD_NAME = ('UNKNOWN', 'VERY_UNLIKELY', 'UNLIKELY', 'POSSIBLE','LIKELY', 'VERY_LIKELY')

def main(args):
  # formatting result
  result = {}
  for type in RESPONSE_TYPE:
    result[type] = {}
    for name in LIKEHOOD_NAME:
      result[type][name] = []
      result[type][name + '_COUNT'] = 0 

  res = requests.get(SLACK_URL.format(slack=args.slack, token=args.token))

  # Google Cloud Vision API Client
  client = vision.ImageAnnotatorClient()
  image = types.Image()

  if res.status_code == 200:
    emoji = res.json().get('emoji', {})
    for k, v in emoji.items():
      image.source.image_uri = v
      logging.info('requesting... safe_search emoji: ' + k)
      gooleo_res = client.safe_search_detection(image=image)

      safe = gooleo_res.safe_search_annotation
      result['adult'][LIKEHOOD_NAME[safe.adult]].append(k)
      result['adult'][LIKEHOOD_NAME[safe.adult] + "_COUNT"] += 1
      result['spoof'][LIKEHOOD_NAME[safe.spoof]].append(k)
      result['spoof'][LIKEHOOD_NAME[safe.spoof] + "_COUNT"] += 1
      result['medical'][LIKEHOOD_NAME[safe.medical]].append(k)
      result['medical'][LIKEHOOD_NAME[safe.medical] + "_COUNT"] += 1
      result['violence'][LIKEHOOD_NAME[safe.violence]].append(k)
      result['violence'][LIKEHOOD_NAME[safe.violence] + "_COUNT"] += 1
      result['racy'][LIKEHOOD_NAME[safe.racy]].append(k)
      result['racy'][LIKEHOOD_NAME[safe.racy] + "_COUNT"] += 1
      
    result_print(result)

  else:
    logging.warning("can't get emoji list")


def result_print(result):
  print('----------- result ---------------')
  for type in RESPONSE_TYPE:
    print(type + ':')
    print('  VERY_LIKELY: ' + unicode_array_to_str(result[type]['VERY_LIKELY']))
    print('       LIKELY: ' + unicode_array_to_str(result[type]['LIKELY']))
    print('     POSSIBLE: ' + unicode_array_to_str(result[type]['POSSIBLE']))
    print('')
    print('  statistics:')
    for name in LIKEHOOD_NAME: 
      print('    ' + '{0:>13}'.format(name) + ': ' + str( result[type][name + '_COUNT']))
    print('')

def unicode_array_to_str(array):
  str = ', '.join(array)
  return '[' + str + ']'

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('slack', help='name of your slack group.')
  parser.add_argument('token', help='auth token for slack.')
  args = parser.parse_args()
  main(args)
