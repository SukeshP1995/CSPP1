import os.path, subprocess
from subprocess import STDOUT,PIPE
import re
import sys
import platform
import os.path
import hashlib
import base64
# import crypt
def get_platform():
    platforms = {
        'linux1' : 'Linux',
        'linux2' : 'Linux',
        'darwin' : 'OS X',
        'win32' : 'Windows'
    }
    if sys.platform not in platforms:
        return sys.platform
    return platforms[sys.platform]

def check_git():
    try:
        run_proc = subprocess.Popen('git', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except Exception as e:
        return False

def check_if_repo():
    run_proc = subprocess.Popen('git status', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = run_proc.communicate()
    if stderr: return False
    return True

def check_if_user():
    run_proc = subprocess.Popen('git config user.name', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = run_proc.communicate()
    if stdout: return True
    return False

def check_push():
    # try:
    run_proc = subprocess.Popen('git push -u origin master', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = run_proc.communicate()
    print(str(stdout.decode('utf-8')) + '->' + str(stderr.decode('utf-8')))
        # if stderr:
        #     return True
        # return True
    # except Exception('e'):
    #     return False

def runProcess(command, expr=None):
    run_proc = subprocess.Popen(command, stdout=subprocess.PIPE)
    proc_out = run_proc.stdout.read().decode('utf-8')
    print(proc_out)
    if expr:
        proc_out = re.findall(expr, proc_out)
        if proc_out:
            tests_passed = int(float(proc_out[0][0]))
            tests_total = int(float(proc_out[0][1]))
            return (tests_passed, tests_total)

def which_python():
    if (sys.version_info > (3, 0)):
        return 3
    else:
        return 2

python_version = which_python()

def computeMD5hash(stringg):
    m = hashlib.md5()
    if python_version == 2:
        m.update(stringg.encode('utf8'))
    else:
        m.update(stringg)
    return m.hexdigest()

def get_content(filename):
    with open(filename, "rb") as f:
        return f.read()

def execute(file, stdin):
    filename,ext = os.path.splitext(file)
    if ext == ".java":
        subprocess.check_call(['javac', "Solution.java"])     #compile
        cmd = ['java', "Solution"]                     #execute
    elif ext == ".c":
        subprocess.check_call(['gcc',"-o","Solution","Solution.c"])     #compile
        if(platform.system() == "Windows"):
            cmd = ['Solution']              #execute for windows OS.
        else:
            cmd = ['./Solution']            #execute for other OS versions
    else:
        cmd = ['python', file]
    proc = subprocess.Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    stdout,stderr = proc.communicate(stdin)
    return stdout

def run_test(testcase_input,testcase_output):
    input1 = get_content(testcase_input)
    md5input = get_content("md5/"+testcase_input)
    output = get_content(testcase_output)
    md5output = get_content("md5/"+testcase_output)
    your_output = execute(program_name, input1)

    if python_version == 3:
        md5input = md5input.decode('utf-8')
        md5output = md5output.decode('utf-8')

    if computeMD5hash(input1) != md5input or computeMD5hash(output) != md5output:
        # print(computeMD5hash(input),crypt.computeMD5hash1(input),computeMD5hash(output),crypt.computeMD5hash1(output))
        return False

    if python_version == 3:
        your_output = your_output.decode('UTF-8').replace('\r','').rstrip() #remove trailing newlines, if any
        output = output.decode('UTF-8').replace('\r','').rstrip()
    else:
        your_output = your_output.replace('\r','').rstrip() #remove trailing newlines, if any
        output = output.replace('\r','').rstrip()

    return input1,output,your_output,output==your_output

def run_tests(inputs,outputs,extension):
    passed = 0
    for i in range(len(inputs)):
        result = run_test(inputs[i],outputs[i])
        if result == False:
            print("########## Testcase "+str(i)+": Failed ##########")
            print("Something is wrong with the testcase.\n")
        elif result[3] == True:
            print("########## Testcase "+str(i)+": Passed ##########")
            print("Expected Output: ")
            print(result[1]+"\n")
            print("Your Output: ")
            print(result[2]+"\n")
            passed+=1
        else:
            print("########## Testcase "+str(i)+": Failed ##########")
            print("Expected Output: ")
            print(result[1]+"\n")
            print("Your Output: ")
            print(result[2]+"\n")
        print("----------------------------------------")
    print("Result: "+str(passed)+"/"+str(len(inputs))+" testcases passed.")
    return (passed, len(inputs))

inputs = []
outputs = []

# populate input and output lists
for root,dirs,files in os.walk('.'):
    for file in files:
        if 'input' in file and '.txt' in file and "md5" not in file:
            inputs.append(file)
        if 'output' in file and '.txt' in file and "md5" not in file:
            outputs.append(file)
    break

# if get_platform() == 'Windows':
if not check_git():
    raise Exception('git not available')

if not check_if_repo():
    raise Exception('You are not in git repo')

if not check_if_user():
    raise Exception('user not logged in')

inputs = sorted(inputs)
outputs = sorted(outputs)

if len(sys.argv)==2 and os.path.isfile(sys.argv[1]):
    if sys.argv[1].endswith(".java"):
        program_name = sys.argv[1]
        extension = ".java"
        result = run_tests(inputs,outputs,extension)

    elif sys.argv[1].endswith(".py"):
        program_name = sys.argv[1]
        extension = ".py"
        result = run_tests(inputs,outputs,extension)
    elif sys.argv[1].endswith(".c"):
        program_name = sys.argv[1]
        extension = ".c"
        result = run_tests(inputs,outputs,extension)
    elif sys.argv[1] == "eval.py":
        print("eval.py cannot be passed as argument")
    else:
        print("Invalid Extension.\nPass only .java or .py files")
else:
    print("File not found.\nPass a valid filename with extension as argument.\npython eval.py <filename>")

cases, totalcases = result
score, totalscore = runProcess("pylint Solution.py","Your code has been rated at (.*)/(.*) \(.*\)")
path = os.getcwd().split('\\')
msg = path[-3] +' '+ path[-1]
runProcess("git commit -am \""+ msg +" -> " + str(cases) + " of " + str(totalcases) + " passed." + " pylint: " + str(score) + "/" + str(totalscore) + " \"")
if not check_push():
    print('Please connect to internet to push and submit your program')
