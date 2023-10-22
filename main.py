import csv
from datetime import datetime


class JefitSetting:
    def __init__(self, mass) -> None:
        self.mass = mass

    def __str__(self) -> str:
        return f"Mass: {self.mass}"


class JefitRoutines:
    def __init__(self, id, name) -> None:
        self.id = id
        self.name = name
        self.workout_sessions = []

    def __str__(self) -> str:
        _str = f"{self.id}: {self.name}:\n"
        for workout_session in self.workout_sessions:
            _str += f"\t{workout_session}\n"
        return _str

    def add_workout_session(self, workout_session):
        self.workout_sessions.append(workout_session)


class JefitWorkoutSession:

    def __init__(self, id, start_time) -> None:
        self.id = id
        self.start_time = start_time
        self.exercises = []
        self.cardio_logs = []

    def __str__(self) -> str:
        _str = f"Workout session at {self.start_time}:\n"
        for exercise in self.exercises:
            _str += f"\t{exercise}\n"

        for cardio_log in self.cardio_logs:
            _str += f"\t{cardio_log}\n"
        return _str

    def add_exercise(self, exercise):
        self.exercises.append(exercise)

    def add_cardio_log(self, cardio_log):
        self.cardio_logs.append(cardio_log)


class JefitExerciseLog:
    def __init__(self, ename, logs) -> None:
        self.ename = ename
        self.logs = logs

    def __str__(self) -> str:
        return f"{self.ename}: {self.logs}"


class JefitExercise:
    def __init__(self, name, notes) -> None:
        self.name = name
        self.notes = notes

    def __str__(self) -> str:
        return f"{self.name}: {self.notes}"


class JefitCardioLog:
    def __init__(self, id, eid, duration, distance, date) -> None:
        self.id = id
        self.eid = eid
        self.duration = duration
        self.distance = distance
        self.date = date

    def __str__(self) -> str:
        return f"{self.eid}: {self.duration} seconds, {self.distance} meters"


class JefitNote:
    def __init__(self, eid, notes, date) -> None:
        self.eid = eid
        self.notes = notes
        self.date = date

    def __str__(self) -> str:
        return f"{self.eid}: {self.notes}"


class StrongRow:
    def __init__(self, date_time, workout_name, exercise_name, weight, weight_unit, reps, rpe, distance_unit, seconds, notes, workout_notes, workout_duration) -> None:
        self.date_time = date_time
        self.workout_name = workout_name
        self.exercise_name = exercise_name
        self.weight = weight
        self.weight_unit = weight_unit
        self.reps = reps
        self.rpe = rpe
        self.distance_unit = distance_unit
        self.seconds = seconds
        self.notes = notes
        self.workout_notes = workout_notes
        self.workout_duration = workout_duration


def read_csv(filename):

    setting = None
    routines = dict()
    workout_sessions = dict()
    cardio_logs = []
    notes = []

    with open(filename, 'r', encoding="utf-8") as f:
        csv_reader = csv.reader(f, delimiter=',')

        for line in csv_reader:
            if line:  # if line is not empty
                if "mass" in line:
                    line = next(csv_reader)  # skips header and gets data
                    setting = JefitSetting(line[8])

                elif "rest_day" in line:  # routines
                    line = next(csv_reader)
                    routine_id = line[4]  # _id value in csv
                    name = line[5]  # name value in csv

                    routine = JefitRoutines(routine_id, name)
                    # Adds routine to dictionary
                    routines[routine.id] = routine

                elif "workout_time" in line:  # workout sessions
                    line = next(csv_reader)

                    # While line is not empty (marks the end of the exercise entries)
                    while (line):
                        workout_id = line[1]        # _id value in csv
                        routine_id = line[4]        # day_id value in csv
                        # starttime value in csv (epoch time)
                        epoch_start_time = line[12]

                        # Converts epoch time to DateTime with format DD/MM/YYYY HH:MM
                        datetime_start_time = epoch_to_datetime(
                            epoch_start_time)

                        # Creates workout session object and adds it to dictionary
                        workout_session = JefitWorkoutSession(
                            workout_id, datetime_start_time)
                        workout_sessions[workout_id] = workout_session

                        try:
                            # Gets routine from dictionary
                            routine = routines[routine_id]
                            # Adds workout session to routine
                            routine.add_workout_session(workout_session)

                        # There might be a workout session from a deleted routine (that routine has no id)
                        except KeyError:
                            pass

                        line = next(csv_reader)  # Gets next line

                # Exercise logs
                elif "belongsession" in line:
                    line = next(csv_reader)  # Skips header
                    while (line):
                        logs_str = line[4]              # logs value in csv
                        exercise_name = line[9]         # ename value in csv
                        # session_id value in csv
                        workout_session_id = line[11]

                        """
                        Splits logs string into list of logs and removes trailing comma in case there is any
                        (sometimes there is a trailing comma without any further data)
                        """
                        logs = logs_str.rstrip(",").split(",")
                        exercise_log = JefitExerciseLog(exercise_name, logs)

                        # Adds exercise log to workout session
                        workout_session = workout_sessions[workout_session_id]
                        workout_session.add_exercise(exercise_log)

                        line = next(csv_reader)

                # Cardio logs
                elif "speed" in line:
                    line = next(csv_reader)
                    while (line):

                        # Gets data from csv
                        _id = line[3]       # _id value in csv
                        eid = line[5]       # eid value in csv
                        duration = line[8]  # duration value in csv
                        distance = line[10]  # distance value in csv
                        date = line[-1]     # date value in csv

                        cardio_log = JefitCardioLog(
                            _id, eid, duration, distance, date)
                        cardio_logs.append(cardio_log)

                        for workout_session in workout_sessions.values():
                            if date in workout_session.start_time:
                                workout_session.add_cardio_log(cardio_log)

                        line = next(csv_reader)

                elif "mynote" in line:
                    line = next(csv_reader)
                    while (line):

                        # Gets data from csv
                        eid = line[4]   # eid value in csv
                        text = line[6]  # mynote value in csv
                        date = line[8]  # mydate value in csv

                        note = JefitNote(eid, text, date)
                        notes.append(note)

                        line = next(csv_reader)


def epoch_to_datetime(epoch_time):
    return datetime.fromtimestamp(int(epoch_time)).strftime("%d/%m/%Y %H:%M")


def main():
    read_csv("data.csv")

if __name__ == "__main__":
    main()
