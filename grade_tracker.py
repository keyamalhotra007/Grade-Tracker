import json #JSON represents data as key-value pairs, arrays, or nested objects

try:
    with open("grades.json", 'r') as file:
        data = json.load(file) #read and parse data from a JSON file, converting it into a Python dictionary.
except (FileNotFoundError, json.JSONDecodeError): #does not exist, file exists but contains invalid JSON
    data = {} #it initializes data as an empty dictionary.


def save_data():
    '''
    Save the current state of the data dictionary to the JSON file.
    '''
    with open("grades.json", 'w') as file:
        json.dump(data, file, indent=4) # It converts the Python object into a JSON-formatted string and saves it in the specified file.


def add_name(name):
    '''
    if the name is not in data: add name
    if the name is alreadt in the data: print "Student already exists"
    '''
    if name not in data:
        data[name] = {} # Adds the name as a key with an empty dictionary as the value
        print(f"Added new student: {name}")
        save_data()
    else:
        print("Student already exists.")


def add_course(name, course_name, num_tests):
    """
    ask for name
    if name not in data: first add name
    if name in data: access it and add course name 
    data --> name --> course name --> remaining percent, remaining no. of tests to add
    """
    if name not in data:
        add_name(name) # Ensures the student is added if not already in the data
    data[name][course_name] = {
        "remaining_percent": 100, # Initial remaining percentage
        "remaining_tests": num_tests, # Number of tests to be added
        "tests": {} # Dictionary to store test details
    }

def add_weightage(name, course_name, num_tests):
    '''
    test name = [weightage, score]
    '''
    while True:
        total_weight = 0
        tests = {}
        error_occurred = False


        print(f"\nEnter weightages for {num_tests} tests.")
        for i in range(num_tests):
            test_name = input(f"Enter name for test #{i+1}: ").strip().lower()
            if test_name in tests:
                print("Test name already entered. Try again.")
                error_occurred = True
                break #exists the for loop

            try:
                weight = float(input(f"Enter weightage for '{test_name}': "))
                if weight <= 0:
                    print("Weightage must be greater than 0.")
                    error_occurred = True
                    break #exists for loop
            except ValueError:
                print("Invalid input. Please enter a number.")
                error_occurred = True
                break #exists the for loop

            tests[test_name] = [weight, None, None]
            total_weight += weight

        if error_occurred:
            print("An error occurred. Please re-enter all test details.\n")
            continue

        if total_weight == 100:
            data[name][course_name]["tests"] = tests
            print("Weights added successfully.\n")
            save_data()
            break  # exit while True loop

        else:
            print(f"\nTotal weightage is {total_weight}, which is not 100.\n")
            print("Options:")
            print("1. Exit")
            print("2. Re-enter all weightages")
            print("3. Change weightage of one test")

            option = input("Enter your choice (1/2/3): ").strip()

            if option == '1':
                return
            elif option == '2':
                continue
            elif option == '3':
                while True:
                    test_to_change = input("Enter the test name to change weightage: ").strip().lower()
                    if test_to_change not in tests:
                        print("Test not found.")
                        continue

                    try:
                        new_weight = float(input(f"Enter new weightage for '{test_to_change}': "))
                        if 0 < new_weight <= 100:
                            tests[test_to_change][0] = new_weight
                        else:
                            print("Enter appropriate weightage (0-100).")
                            continue
                    except ValueError:
                        print("Invalid input. Please enter a numeric value.")
                        continue

                    # Recalculate total weight
                    total_weight = sum(test[0] for test in tests.values())
                    print(f"Updated total weightage: {total_weight}")

                    if total_weight == 100:
                        data[name][course_name]["tests"] = tests
                        print("Weights updated successfully.\n")
                        save_data()
                        return
                    else:
                        print("Still not 100. Fix another test or try again.")
            else:
                print("Invalid option. Try again.\n")


    
def add_score(name, course_name, test_name, score):
    '''
    test_name = [weight, required, score]
    '''
    try:
        if test_name not in data[name][course_name]["tests"]:
            print("Test not found in this course.")
            return
        
        if not (0 <= score <= 100):
            print("Score must be between 0 and 100.")
            return

        data[name][course_name]["tests"][test_name][1] = None
        data[name][course_name]["tests"][test_name][2] = score
        
        update_required(name, course_name)

        save_data()

        print(f"Score for '{test_name}' updated for {name} in '{course_name}'.")

    except KeyError:
        print("Student or course not found.")


def update_required(name, course_name):
    '''
    Calculate the required scores for remaining tests to meet the goal.
    '''
    
    goal = data[name][course_name].get("goal", 0) # Retrieve the goal percentage set for the course. If not set, default to 0.
    total_score = 0 
    remaining_weight = 0  

    # Loop through each test in the course to calculate the current total score and remaining weight
    for test_name, [weight, required, score] in data[name][course_name]["tests"].items():
        if score is not None:
            # Calculate the weighted score for the test and add it to the total score
            total_score += (weight * score) / 100  
        else: #If score is None, add the weight of this test to the remaining weight
            remaining_weight += weight

    for test_name, [weight, required, score] in data[name][course_name]["tests"].items():
        if score is None:  # Only calculate the requirement for tests without a score
            if remaining_weight > 0:  #As long as no weights are left
                required = (goal - total_score) / (remaining_weight / 100)
                if required > 100:
                    print(f"Required score for remaining tests is {required:.2f}%, which is not achievable.")
                    choice = input("Do you want to update the goal? (yes/no): ").strip().lower()
                    if choice == "yes":
                        add_goal(name, course_name)
                        return #Stops executing rest of function
                data[name][course_name]["tests"][test_name][1] = round(required, 2) #only print 2 decimal places
            else:
                data[name][course_name]["tests"][test_name][1] = None

    save_data()

def add_goal(name, course_name):
        try:
            goal = float(input("What is your goal percentage for this course? "))
            if 0 <= goal <= 100:
                data[name][course_name]["goal"] = goal
                update_required(name, course_name)
                print(f"Goal of {goal}% set for {course_name}.")
                return
        except ValueError:
            print("Invalid input for goal percentage. Please enter a number.")


def clear_data():
    choice = input("Enter name to clear data or type 'all' to clear all data: ")
    if choice.lower() == "all":
        data.clear() #clear all
        print("All data cleared.")
    elif choice in data:
        sub_choice = input("Enter 'all' to clear all courses or type course name to clear that course: ")
        if sub_choice.lower() == "all":
            data.pop(choice) #pop --> remove and return 
            print(f"All data for {choice} cleared.")
        elif sub_choice in data[choice]:
            del data[choice][sub_choice] #del --> delete
            print(f"Course '{sub_choice}' cleared for {choice}.")
        else:
            print("Course not found.")
    else:
        print("Name not found.")
    save_data()

def view_grades(name):

    if name not in data:
        print("Student not found.")
        return
    
    if not data[name]: 
        print("\nNo courses added for this student")
        return
    
    print(f"\nGrades for {name}:")
    for course, details in data[name].items():
        print(f"\nCourse: {course}")
        if "tests" not in details or not details["tests"]:
            print("Course not found.")
            continue
        
        print("Tests:")
        for test_name, (weight, required, score) in details["tests"].items():
            print(f"\n{test_name}")
            print(f"Score: {score if score is not None else 'None'}")
            # Only print 'Required' if it's not None
            if score is None and required is not None:
                print(f"Required: {required}")

def main():
    while True:
        print()
        print("1. Add Student")
        print("2. Add Course")
        print("3. Add Goal")
        print("4. Add/Update Score")
        print("5. View Grades")
        print("6. Clear Data")
        print("7. Quit")

        choice = input("Enter option: ")

        if choice == "1":
            name = input("Enter student name: ").lower()
            add_name(name)

        elif choice == "2":
            name = input("Enter student name: ").lower()
            course_name = input("Enter course name: ").lower()
            num_tests = int(input("Enter number of tests: "))
            add_course(name, course_name, num_tests)
            add_weightage(name, course_name, num_tests)

        elif choice == "3":
            name = input("Enter student name: ").lower()
            if name not in data:
                print("Student not found.")
                continue

            if not data[name]:
                print("No courses added for this student")
                continue
            
            course_name = input("Enter course name: ").lower()
            if course_name not in data[name]:
                print("Course not found. Please try again.")
                continue
            
            add_goal(name, course_name)

        elif choice == "4":
            name = input("Enter student name: ").lower()
            while name not in data:
                print("Name not in data")
                name = input("Enter student name: ").lower()

            course_name = input("Enter course name: ").lower()
            while course_name not in data[name]:
                print("Course name not in data")
                course_name = input("Enter course name: ").lower()

            test_name = input("Enter test name: ").lower()
            while test_name not in data[name][course_name]["tests"]:
                    print("Test name not in data")
                    test_name = input("Enter test name: ").lower()

            score = int(input("Enter score: "))
            add_score(name, course_name, test_name, score)

            
        elif choice == "5":
            name = input("Enter student name: ").lower()
            view_grades(name)

        elif choice == "6":
             clear_data()

        elif choice == "7":
            print("Goodbye!")
            break

        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    main()
