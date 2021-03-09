# Copyright 2021 Edward Leardi. All Rights Reserved.
#
# Copyright 2020 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"Script for sending a message to our gitter channel."

# To update token, go to https://developer.gitter.im/apps and copy token to the github repository secret GITTER_TOKEN
# To update room, find Gitter room id using Gitter API and copy id to the github repository secret GITTER_ROOM_ID

import os
import requests


GITTER_TOKEN = os.getenv('token')
GITTER_ROOM_ID = os.getenv('room-id')
GITTER_TEXT = os.getenv('text')
GIT_REF = os.getenv('GITHUB_REF')
GIT_SHA = os.getenv('GITHUB_SHA')
GITHUB_REPOSITORY = os.getenv('GITHUB_REPOSITORY')
GITHUB_SERVER_URL = os.getenv('GITHUB_SERVER_URL')
GITHUB_RUN_ID = os.getenv('GITHUB_RUN_ID')

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': f"Bearer {GITTER_TOKEN}",
}

data = (
    f'{{"text":"**{GITHUB_REPOSITORY}**\\n\\n'
    f'{GITTER_TEXT}\\n'
    f'{GIT_REF}:{GIT_SHA}\\n'
    f'{GITHUB_SERVER_URL}/{GITHUB_REPOSITORY}/actions/runs/{GITHUB_RUN_ID}"}}'
)

response = requests.post(f'https://api.gitter.im/v1/rooms/{GITTER_ROOM_ID}/chatMessages', headers=headers, data=data)
