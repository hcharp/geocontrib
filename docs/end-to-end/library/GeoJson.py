# Copyright (c) 2017-2021 Neogeo-Technologies.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


import selenium

from utils import get_driver


def geo_json_export():
    get_driver().find_element_by_xpath("//img").click()
    get_driver().find_element_by_link_text(
        u"Pour test de création de signalement"
    ).click()
    get_driver().find_element_by_link_text(
        u"Pour test de création de signalement"
    ).click()
    get_driver().find_element_by_link_text("Exporter").click()
    get_driver().find_element_by_xpath("//div[3]/div/div").click()


def geo_json_import():
    get_driver().find_element_by_xpath(
        "//form[@id='form-import-features']/div/label/span"
    ).click()
    get_driver().find_element_by_id("json_file").clear()
    get_driver().find_element_by_id("json_file").send_keys("export_projet.json")
    get_driver().find_element_by_xpath("//button[@type='submit']").click()
