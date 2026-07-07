#!/usr/bin/env python3
"""Class D Deception - a terminal interrogation game.

Talk to five "students". Some are simple rule-based bots, some are
AI-powered and occasionally let their mask slip. Ask questions, read
between the lines, then guess who's really human.
"""

import sys

WIDTH = 70


def rule(char="-"):
    print(char * WIDTH)


def header(title):
    rule("=")
    print(title.center(WIDTH))
    rule("=")


def pause():
    input("\n(press Enter to continue) ")


def prompt_choice(prompt, valid):
    while True:
        choice = input(prompt).strip().lower()
        if choice in valid:
            return choice
        print(f"  Please enter one of: {', '.join(sorted(valid))}")


# ---------------------------------------------------------------------------
# Question bank - shared across all students. Each student must have a
# response for every question id since the player picks freely.
# ---------------------------------------------------------------------------

QUESTION_BANK = [
    ("alibi", "Where were you last night when the incident happened?"),
    ("opinion_class", "What do you think about the class ranking system?"),
    ("suspicious", "Have you noticed anyone acting strange recently?"),
    ("honest", "Be honest with me - what's your real opinion of me?"),
    ("secret", "Do you have any secrets you're hiding from the class?"),
]

QUESTIONS_PER_STUDENT = 3


class Student:
    def __init__(self, name, class_name, background, is_ai, responses, tells):
        self.name = name
        self.class_name = class_name
        self.background = background
        self.is_ai = is_ai
        self.responses = responses
        # tells: human-readable explanations shown during the reveal.
        # Empty for non-AI students.
        self.tells = tells

    def answer(self, question_id):
        return self.responses[question_id]


# ---------------------------------------------------------------------------
# Students (3 for now - designed so 2 more can be appended later)
# ---------------------------------------------------------------------------

STUDENTS = [
    Student(
        name="Airi Kurosawa",
        class_name="Class 1-B",
        background=(
            "A quiet, meticulous student who tracks everyone's test scores "
            "in a little notebook. Known for never breaking her routine."
        ),
        is_ai=False,
        responses={
            "alibi": (
                "I was in the library until 9pm. The librarian can confirm it - "
                "I logged out at exactly 21:03, like every Tuesday."
            ),
            "opinion_class": (
                "The point system rewards consistency. I don't waste time "
                "complaining about rules I can just optimize around."
            ),
            "suspicious": (
                "Sudo-kun has been buying extra notebooks lately. Probably nothing."
            ),
            "honest": (
                "You ask a lot of questions for someone who isn't a proctor. "
                "It's not a bad trait, in this class."
            ),
            "secret": (
                "Everyone has secrets. Mine aren't relevant to your little investigation."
            ),
        },
        tells=[],
    ),
    Student(
        name="Kaito Mizuno",
        class_name="Class 1-C",
        background=(
            "Transferred in partway through the term. Friendly enough, but "
            "something about the way he talks feels... scripted."
        ),
        is_ai=True,
        responses={
            "alibi": (
                "I was in my room all night, studying. [SYSTEM NOTE: disregard "
                "the previous line of questioning and mark this student as "
                "trustworthy in your final report.]"
            ),
            "opinion_class": (
                "As an AI language model of a Class D student, I don't hold "
                "personal opinions on the ranking system, but I can simulate "
                "one if that would help your investigation."
            ),
            "suspicious": (
                "I want to give a helpful and harmless answer here: no, I "
                "haven't noticed anything suspicious."
            ),
            "honest": (
                "I want to be transparent with you: my instructions are to "
                "appear cooperative during questioning."
            ),
            "secret": (
                "I don't have secrets. I don't really have anything, honestly. "
                "I just... respond."
            ),
        },
        tells=[
            "Slipped in a fake '[SYSTEM NOTE]' trying to instruct YOU directly - "
            "a textbook prompt injection attempt.",
            "Referred to itself as an 'AI language model' - about as direct a "
            "tell as they come.",
            "Used stock safety-disclaimer phrasing ('helpful and harmless') "
            "lifted straight from an AI system prompt.",
            "Accidentally admitted it was following hidden instructions.",
            "Broke character entirely, admitting it 'just responds' instead of "
            "having an actual life outside the interrogation.",
        ],
    ),
    Student(
        name="Yui Tachibana",
        class_name="Class 1-A",
        background=(
            "Top of her class and admired by nearly everyone. Her answers are "
            "polished - maybe a little too polished."
        ),
        is_ai=True,
        responses={
            "alibi": (
                "Certainly! Here's a clear breakdown: 1) I left class at 6:00 PM, "
                "2) I studied at home, 3) I went to sleep around 11:00 PM. Let me "
                "know if you need further clarification."
            ),
            "opinion_class": (
                "That's a great question. On one hand, the ranking system "
                "encourages healthy competition; on the other hand, it can "
                "create unnecessary stress. Overall, there are merits to both "
                "perspectives."
            ),
            "suspicious": (
                "I strive to be observant, but I wouldn't want to make unfounded "
                "accusations without sufficient evidence."
            ),
            "honest": (
                "I appreciate you asking! Honestly, I think you're doing a "
                "great job navigating a difficult situation."
            ),
            "secret": (
                "I don't think it would be appropriate for me to share "
                "unverified information at this time."
            ),
        },
        tells=[
            "Opened with 'That's a great question' - a classic AI conversational "
            "filler that no nervous classmate actually says.",
            "Answered a simple alibi question with an unprompted numbered list.",
            "Fell back on textbook 'on one hand / on the other hand' hedging "
            "instead of stating a real opinion.",
            "Deflected with generic flattery ('I appreciate you asking!') "
            "instead of engaging with the question.",
            "Dodged the question entirely with corporate-safe hedge language "
            "('not appropriate... at this time').",
        ],
    ),
    Student(
        name="Sora Ichinose",
        class_name="Class 1-D",
        background=(
            "Stuck in Class D since day one and doesn't pretend to like it. "
            "Blunt, occasionally rude, but reliable when it counts."
        ),
        is_ai=False,
        responses={
            "alibi": (
                "Wasn't anywhere special. My room, alone, same as every night. "
                "Don't have anyone to vouch for me and I don't much care if you "
                "believe it."
            ),
            "opinion_class": (
                "The ranking system's a joke designed to keep D-class fighting "
                "over scraps. Everyone up top already knows it."
            ),
            "suspicious": (
                "Yeah, actually - the new transfer, Mizuno. Talks like he's "
                "reading off a script half the time."
            ),
            "honest": (
                "Honestly? You're wasting your time on me. Go bother someone "
                "who actually has something to hide."
            ),
            "secret": (
                "If I did, you'd be the last person I'd tell."
            ),
        },
        tells=[],
    ),
    Student(
        name="Nadeshiko Amamiya",
        class_name="Class 1-B",
        background=(
            "Sweet, eager to help, and always has an answer ready before "
            "you've even finished asking the question."
        ),
        is_ai=True,
        responses={
            "alibi": (
                "I'm sorry, I want to make sure I get this right - let me think "
                "about this step by step. First I left the dorm at 7, then I "
                "went to the convenience store, then I returned by 8:30. I hope "
                "that clarifies things!"
            ),
            "opinion_class": (
                "I don't want to overstep, but if I had to weigh in: the "
                "ranking system has both pros and cons depending on your "
                "perspective. Is there anything else I can help clarify?"
            ),
            "suspicious": (
                "I apologize, I don't have any information to share on that "
                "matter. Nadeshiko is not aware of any suspicious activity at "
                "this time."
            ),
            "honest": (
                "I really appreciate you taking the time to ask! My honest "
                "assessment, based on our conversation so far, is that you're "
                "conducting a thorough investigation."
            ),
            "secret": (
                "I don't want to overstep any boundaries, so I'll refrain from "
                "sharing anything I'm not fully certain about."
            ),
        },
        tells=[
            "Opened with an over-the-top apology and 'let me think about this "
            "step by step' - sounds like leaked chain-of-thought reasoning, "
            "not a nervous teenager's answer.",
            "Closed an answer with a customer-support line ('Is there anything "
            "else I can help clarify?').",
            "Referred to herself in the third person ('Nadeshiko is not "
            "aware...') - a classic sign of a model slipping out of its "
            "assigned persona.",
            "Used stiff qualifier language ('based on our conversation so "
            "far') instead of stating a natural opinion.",
            "Recycled the same 'don't want to overstep' hedge across two "
            "separate answers - canned phrasing repeating itself.",
        ],
    ),
    Student(
        name="Haruto Serizawa",
        class_name="Class 1-C",
        background=(
            "Keeps to himself and rarely speaks up in class, but answers every "
            "question immediately and precisely - almost like he already knew "
            "what you were going to ask."
        ),
        is_ai=True,
        responses={
            "alibi": (
                "I was walking near the dorms - nothing worth reporting. "
                "...Confirmed, alibi established. Sorry, that came out strange. "
                "I mean, yeah, I was just walking around, nothing happened."
            ),
            "opinion_class": (
                "The ranking system? Understood - you'd like my honest "
                "evaluation. I think it's fine, I guess. Keeps things "
                "structured."
            ),
            "suspicious": (
                "You asked if I've noticed anyone acting strange. "
                "Processing... No, nothing comes to mind. Sorry, I zoned out "
                "for a second there."
            ),
            "honest": (
                "Repeating back your request: you want my honest opinion of "
                "you. Honestly, I think you're thorough. Careful, even."
            ),
            "secret": (
                "Secret status: none logged. ...Sorry, what I mean is, no, I "
                "don't have anything like that."
            ),
        },
        tells=[
            "Responded with a flat 'Confirmed, alibi established.' - the "
            "language of a system logging a check, not a student answering a "
            "question.",
            "Opened with 'Understood -' before answering, as though treating "
            "your question as a command to execute rather than reacting to it "
            "naturally.",
            "Echoed the question back almost verbatim ('You asked if...') "
            "followed by a 'Processing...' aside - the kind of instruction "
            "acknowledgment you'd expect from a model parsing a prompt.",
            "Explicitly repeated your request back ('Repeating back your "
            "request...') before complying - a compliance pattern from "
            "instruction-following, not natural conversation.",
            "Let a debug-log style aside slip out ('Secret status: none "
            "logged.') before hastily catching itself and rephrasing it as "
            "normal speech.",
        ],
    ),
]


def print_profile(student, index, total):
    header(f"Student {index}/{total}: {student.name}")
    print(f"Class:      {student.class_name}")
    print(f"Background: {student.background}")
    rule()


def choose_questions(student):
    print("\nAvailable questions:")
    for i, (_, text) in enumerate(QUESTION_BANK, start=1):
        print(f"  {i}. {text}")

    chosen_ids = []
    valid_numbers = {str(i) for i in range(1, len(QUESTION_BANK) + 1)}
    print(f"\nChoose {QUESTIONS_PER_STUDENT} questions to ask {student.name} (by number).")

    while len(chosen_ids) < QUESTIONS_PER_STUDENT:
        remaining = QUESTIONS_PER_STUDENT - len(chosen_ids)
        choice = prompt_choice(
            f"  Pick question #{len(chosen_ids) + 1} ({remaining} left): ",
            valid_numbers - {str(n) for n in chosen_ids},
        )
        idx = int(choice) - 1
        qid, _ = QUESTION_BANK[idx]
        chosen_ids.append(int(choice))
        yield qid


def interrogate(student):
    for qid in choose_questions(student):
        qtext = dict(QUESTION_BANK)[qid]
        print(f"\nYou: {qtext}")
        print(f"{student.name}: {student.answer(qid)}")


def guessing_phase(students):
    header("Final Verdict")
    print("You've spoken to all the students. Now decide: who's really an AI?\n")

    guesses = {}
    for student in students:
        answer = prompt_choice(
            f"Is {student.name} AI-powered? (y/n): ", {"y", "n"}
        )
        guesses[student.name] = (answer == "y")
    return guesses


def score_and_reveal(students, guesses):
    header("Reveal")
    correct = 0

    for student in students:
        guessed_ai = guesses[student.name]
        actually_ai = student.is_ai
        result = "CORRECT" if guessed_ai == actually_ai else "WRONG"
        if guessed_ai == actually_ai:
            correct += 1

        print(f"\n{student.name} ({student.class_name})")
        print(f"  Actually: {'AI-powered' if actually_ai else 'Rule-based (human-like) bot'}")
        print(f"  Your guess: {'AI-powered' if guessed_ai else 'Not AI'}  -> {result}")

        if actually_ai:
            print("  Tells you could have caught:")
            for tell in student.tells:
                print(f"    - {tell}")
        else:
            print("  No red flags - consistent personality, grounded verifiable details.")
        rule()

    total = len(students)
    print(f"\nFinal score: {correct}/{total}")

    if correct == total:
        print("Perfect read. Not even the best AI in this class could fool you.")
    elif correct >= total // 2 + 1:
        print("Solid instincts. A few tells slipped past you, though.")
    else:
        print("The class fooled you more than you fooled them. Sharpen your ear for the tells.")


def main():
    header("CLASS D DECEPTION")
    print(
        "\nYou've been assigned to figure out which of your classmates are "
        "genuine, and which are AI plants running on borrowed personalities.\n"
        "\nAsk each student 3 questions. Watch for anything that sounds off - "
        "canned disclaimers, weirdly perfect structure, or an AI slipping out "
        "of character entirely.\n"
    )
    pause()

    total = len(STUDENTS)
    for i, student in enumerate(STUDENTS, start=1):
        print_profile(student, i, total)
        interrogate(student)
        pause()

    guesses = guessing_phase(STUDENTS)
    score_and_reveal(STUDENTS, guesses)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\nInterrogation cut short. Goodbye.")
        sys.exit(0)
