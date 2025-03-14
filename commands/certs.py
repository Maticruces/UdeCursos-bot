from datetime import datetime
import json
#
from components.fetch import get_generation


def getRemainingDays(subject):
    currentDate = datetime.now().strftime("%Y-%m-%d")
    subjectDate = subject['date']
    remainingDays = (datetime.strptime(subjectDate, "%Y-%m-%d") - datetime.strptime(currentDate, "%Y-%m-%d")).days

    return remainingDays


def certs(update, context):
    with open('data/certs.json') as file:
        data = json.load(file)

    alertMsg = """
⚠️ ¡Asegúrate de seguir el formato!
      _/certs <rango> <ramoI, ramoII ...>_
"""
    noneMsg = """
🙁 ¡Oops! No poseo asignaturas o eventos así hasta la fecha.
"""
    try:
        if context.args[0] == 'help':
            update.message.reply_text(alertMsg, parse_mode='Markdown')
            return
    except IndexError:
        print('[ ! ] No subjects provided')
        pass

    try:
        rango = int(context.args[0])
        if rango > 120:
            rango = 120
    except (IndexError, ValueError):
        rango = 40

    try:
        if not (context.args[0].isdigit()):
            ramosRaw = context.args

        elif (context.args[0].isdigit()):
            if len(context.args) > 1:
                ramosRaw = context.args[1:]
            elif len(context.args) == 1:
                ramosRaw = []
        else:
            update.message.reply_text(alertMsg)
            return


    except IndexError:
        print('[ ! ] Ramos raw now is empty: IndexError with context.args')
        ramosRaw = []

    ramos = []
    for j in ramosRaw:
        try:
            if (j[-1] == 'I') and (j[-2] == 'I'):
                j = j.replace('II', ' II')
                ramos.append(j.lower())
            elif (j[-1] == 'I') and (j[-2] != 'I'):
                j = j.replace('I', ' I')
                ramos.append(j.lower())

            elif (j[-1] == 'i') and (j[-2] == 'i'):
                j = j.replace('ii', ' ii')
                ramos.append(j.lower())
            elif (j[-1] == 'i') and (j[-2] != 'i'):
                j = j.replace('i', ' i')
                ramos.append(j.lower())
            else:
                ramos.append(j.lower())
                pass
        except IndexError:
            ramos.append(j.lower())
            pass

    chat_id = str(update.message.chat_id)
    gen = get_generation(chat_id)
    # groupsIDs = fetch_groups_IDs()

    if gen == None:
        update.message.reply_text(
            "🙁 ¡Oops! No puedo enviarte las asignaturas.\n"
            "Consulta a un administrador para registrar tu grupo de Telegram.",
            parse_mode='Markdown'
        )
        return

    # gen = 'gen2021' if (chat_id == groupsIDs[0] or chat_id == groupsIDs[-1]) else 'gen2022'

    subjectsList = []
    for subject in data[gen]['certs']:
        if getRemainingDays(subject) > rango:
            continue
        if ramos:
            if subject['name'].lower() in ramos:
                subjectsList.append(f"{getRemainingDays(subject)} días - {subject['name']}")
            else:
                continue
        else:
            print("[ ! ] Event mode: Subject not found")
            subjectsList.append(f"{getRemainingDays(subject)} días: ({subject['type']})\n{subject['name']}\n")
    if subjectsList == []:
        update.message.reply_text(noneMsg)
        return
    else:
        subjectsList.sort(key=lambda x: int(x.split(' ')[0]))

    body = f"""
    ✳️ *Próximas Evaluaciones* ✳️
~ Rango: {rango} días

"""

    status = ['🏳', '🔴', '🟠', '🟡', '🟢', 'DONE']
    for subject in subjectsList:
        remaining = int(subject.split(' ')[0])
        if remaining < 0:
            continue
        elif 0 <= remaining <= 2:
            assignedStatus = status[0]
        elif 3 <= remaining <= 7 :
            assignedStatus = status[1]
        elif 8 <= remaining <= 14:
            assignedStatus = status[2]
        elif 15 <= remaining <= 23:
            assignedStatus = status[3]
        else:
            assignedStatus = status[4]

        body += f"• {assignedStatus} _{subject}_\n"


    update.message.reply_text(
        body,
        parse_mode='Markdown'
    )
