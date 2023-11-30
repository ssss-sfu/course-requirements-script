from period import Term, Period, get_current_period
from course import Course, CourseInfo, CourseGroup
from sosy_requirements import software_systems_requirements
from typing import List
import requests
import json

BASE_URL = "http://www.sfu.ca/bin/wcm/course-outlines"
RESULT_FILE_PATH = "result/courses.json"

def get_course_info(subject, number, period=get_current_period()):
    term = period.term.value
    year = period.year
    course_url = f"{BASE_URL}?{year}/{term}/{subject}/{number}"
    course_res = requests.get(course_url)
    if (course_res.status_code == 404):
        # Recurse to previous term until we get info
        return get_course_info(subject, number, period.previous_period())

    # Status Code here is 200 OK
    course_json = json.loads(course_res.text)
    section = course_json[0]['value']
    section_url = f"{course_url}/{section}"
    section_res = requests.get(section_url)
    return json.loads(section_res.text)




json_result = []

for courseGroup in software_systems_requirements:
    course_info_list: List[CourseInfo] = []
    for course in courseGroup.courses:
        print("Fetching - ", course.subject, course.number)
        data = get_course_info(course.subject, course.number)
        course_info = CourseInfo(course, data['info']['title'])
        course_info_list.append(course_info.toJson())

    json_result.append(
        {
            "requirement": courseGroup.name,
            "courses": course_info_list
        }
    )

print("JSON RESULT", json_result)

with open(RESULT_FILE_PATH, 'w') as f:
    json.dump(json_result, f)
