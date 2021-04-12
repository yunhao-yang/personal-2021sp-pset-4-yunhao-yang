from pset_4.tasks.stylize import *
from pset_4.tasks.data import *
import pandas as pd
from csci_utils.io.my_io import atomic_write
from csci_utils.hashing.hash_str import get_user_id
import json
import os
import re
from pprint import pprint
from typing import Dict
from typing import List

from canvasapi import Canvas
from canvasapi.quiz import QuizSubmission
from canvasapi.quiz import QuizSubmissionQuestion
from environs import Env
from git import Repo
from luigi import build
from .tasks.stylize import Stylize
from csci_utils.canvas.my_canvas import MyCourse


def get_answers(questions: List[QuizSubmissionQuestion]) -> List[Dict]:
    """Creates answers for Canvas quiz questions"""
    # Formulate your answers - see docs for QuizSubmission.answer_submission_questions below
    # It should be a list of dicts, one per q, each with an 'id' and 'answer' field
    # The format of the 'answer' field depends on the question type
    # You are responsible for collating questions with the functions to call - do not hard code
    ans = []
    for qu in questions:
        an = {}
        p_id = re.findall('id="(\w+)"', qu.question_text)[0]
        a_id = qu.id
        an["id"] = a_id
        if p_id == "commit":
            repo = Repo(".")
            an["answer"] = repo.head.commit.hexsha
        elif p_id == "clean":
            an["answer"] = 4031
        elif p_id == "hours":
            an["answer"] = 568
        elif p_id == "style":
            an["answer"] = 'out_mj.jpg'
        else:
            raise RuntimeError("Unknown p_id {}".format(p_id))
        ans.append(an)
    return ans
    # eg {"id": questions[0].id, "answer": {key: some_func(key) for key in questions[0].answer.keys()}}


def get_submission_comments(repo: Repo, qsubmission: QuizSubmission) -> Dict:
    """Get some info about this submission"""
    return dict(
        hexsha=repo.head.commit.hexsha[:8],
        submitted_from=repo.remotes.origin.url,
        dt=repo.head.commit.committed_datetime.isoformat(),
        branch=os.environ.get("TRAVIS_BRANCH", None),  # repo.active_branch.name,
        is_dirty=repo.is_dirty(),
        quiz_submission_id=qsubmission.id,
        quiz_attempt=qsubmission.attempt,
        travis_url=os.environ.get("TRAVIS_BUILD_WEB_URL", None),
    )


def main():

    repo = Repo(".")

    # Load environment
    env = Env()
    env.read_env()

    my_course = MyCourse("CSCI E-29")
    course_id = my_course.get_course().id
    assignment_id = my_course.get_assignment_by_name("Pset 4").id
    quiz_id = my_course.get_quiz_by_name("Pset 4 Answers").id
    as_user_id = env.int("CANVAS_AS_USER_ID", 0)  # Optional - for test student

    if as_user_id:
        masquerade = dict(as_user_id=as_user_id)
    else:
        masquerade = {}

    if repo.is_dirty() and not env.bool("ALLOW_DIRTY", False):
        raise RuntimeError(
            "Must submit from a clean working directory - commit your code and rerun"
        )

    # Load canvas objects
    canvas = Canvas(env.str("CANVAS_URL"), env.str("CANVAS_TOKEN"))
    course = canvas.get_course(course_id, **masquerade)
    assignment = course.get_assignment(assignment_id, **masquerade)
    quiz = course.get_quiz(quiz_id, **masquerade)

    # Begin submissions
    url = "https://github.com/csci-e-29/{}/commit/{}".format(
        os.path.basename(repo.working_dir), repo.head.commit.hexsha
    )  # you MUST push to the classroom org, even if CI/CD runs elsewhere (you can push anytime before peer review begins)

    qsubmission = None
    try:
        # Attempt quiz submission first - only submit assignment if successful
        qsubmission = quiz.create_submission(**masquerade)
        questions = qsubmission.get_submission_questions(**masquerade)

        # Get some basic info to help develop
        for q in questions:
            print("{} - {}".format(q.question_name, q.question_text.split("\n", 1)[0]))

            # MC and some q's have 'answers' not 'answer'
            pprint(
                {
                    k: getattr(q, k, None)
                    for k in ["question_type", "id", "answer", "answers"]
                }
            )

            print()

        # Submit your answers
        answers = get_answers(questions)
        pprint(answers)
        responses = qsubmission.answer_submission_questions(
            quiz_questions=answers, **masquerade
        )

    finally:
        if qsubmission is not None:
            completed = qsubmission.complete(**masquerade)

            # Only submit assignment if quiz finished successfully
            submission = assignment.submit(
                dict(
                    submission_type="online_url",
                    url=url,
                ),
                comment=dict(
                    text_comment=json.dumps(get_submission_comments(repo, qsubmission))
                ),
                **masquerade,
            )
    pass
