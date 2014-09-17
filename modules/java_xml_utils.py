import os
import shutil
import tempfile


THIS_LOCATION = os.path.dirname(os.path.realpath(__file__))

JAVA_PATH = 'java'
JAR_TRANSFORM = THIS_LOCATION + '/../../jar/saxonb9-1-0-8j/saxon9.jar'
JAR_VALIDATE = THIS_LOCATION + '/../../jar/XMLCheck.jar'


def remove_doctype(content):
    return replace_doctype(content, '')


def replace_doctype(content, new_doctype):
    if '\n<!DOCTYPE' in content:
        temp = content[content.find('\n<!DOCTYPE'):]
        temp = temp[0:temp.find('>')+1]
        if len(temp) > 0:
            content = content.replace(temp, new_doctype)
    elif content.startswith('<?xml '):
        temp = content
        temp = temp[0:temp.find('?>')+2]
        if len(new_doctype) > 0:
            content = content.replace(temp, temp + '\n' + new_doctype)
    return content


def apply_dtd(xml_filename, doctype):
    temp_filename = tempfile.mkdtemp() + '/' + os.path.basename(xml_filename)
    shutil.copyfile(xml_filename, temp_filename)
    content = replace_doctype(open(xml_filename, 'r').read(), doctype)
    open(xml_filename, 'w').write(content)
    return temp_filename


def restore_xml_file(xml_filename, temp_filename):
    shutil.copyfile(temp_filename, xml_filename)
    os.unlink(temp_filename)
    shutil.rmtree(os.path.dirname(temp_filename))


def format_parameters(parameters):
    r = ''
    for k, v in parameters.items():
        if v != '':
            if ' ' in v:
                r += k + '=' + '"' + v + '" '
            else:
                r += k + '=' + v + ' '
    return r


def xml_content_transform(content, xsl_filename):
    f = tempfile.NamedTemporaryFile(delete=False)
    f.close()
    fp = open(f.name, 'w')
    fp.write(content)
    fp.close()
    f2 = tempfile.NamedTemporaryFile(delete=False)
    f2.close()
    if xml_transform(f.name, xsl_filename, f2.name):
        fp = open(f2.name, 'r')
        content = fp.read()
        fp.close()
        os.unlink(f2.name)
    if os.path.exists(f.name):
        os.unlink(f.name)
    return content


def xml_transform(xml_filename, xsl_filename, result_filename, parameters={}):
    error = False

    temp_result_filename = tempfile.mkdtemp() + '/' + os.path.basename(result_filename)
    if not os.path.isdir(os.path.dirname(result_filename)):
        os.makedirs(os.path.dirname(result_filename))
    for f in [result_filename, temp_result_filename]:
        if os.path.isfile(f):
            os.unlink(f)

    temp_xml_filename = apply_dtd(xml_filename, '')

    cmd = JAVA_PATH + ' -jar ' + JAR_TRANSFORM + ' -novw -w0 -o "' + temp_result_filename + '" "' + xml_filename + '"  "' + xsl_filename + '" ' + format_parameters(parameters)
    #print(cmd)
    os.system(cmd)
    if not os.path.exists(temp_result_filename):
        print('  ERROR: Unable to create ' + os.path.basename(result_filename))
        open(temp_result_filename, 'w').write('ERROR: transformation error.\n' + cmd)
        error = True
    shutil.move(temp_result_filename, result_filename)
    restore_xml_file(xml_filename, temp_xml_filename)

    return (not error)


def xml_validate(xml_filename, result_filename, doctype=None):
    validation_type = ''
    temp_xml_filename = ''
    if doctype is not None:
        validation_type = '--validate'
        temp_xml_filename = apply_dtd(xml_filename, doctype)

    temp_result_filename = tempfile.mkdtemp() + '/' + os.path.basename(result_filename)
    if os.path.isfile(result_filename):
        os.unlink(result_filename)
    if not os.path.isdir(os.path.dirname(result_filename)):
        os.makedirs(os.path.dirname(result_filename))

    cmd = JAVA_PATH + ' -cp ' + JAR_VALIDATE + ' br.bireme.XMLCheck.XMLCheck ' + xml_filename + ' ' + validation_type + '>"' + temp_result_filename + '"'
    os.system(cmd)

    result = ''
    if os.path.exists(temp_result_filename):
        if 'ERROR' in result.upper():
            n = 0
            s = ''
            for line in open(xml_filename, 'r').readlines():
                if n > 0:
                    s += str(n) + ':' + line
                n += 1
            result += '\n' + s
    else:
        result = 'ERROR: Not valid. Unknown error.\n' + cmd

    if 'ERROR' in result.upper():
        open(temp_result_filename, 'a+').write(result)
        valid = False
    else:
        valid = True

    shutil.move(temp_result_filename, result_filename)
    shutil.move(temp_xml_filename, xml_filename)
    return valid
