
def format_datetime(value, format='short'):
    """Filtro que transforma un datetime en str con formato.

    El filtro es para ser usado en plantillas JINJA2.
    Los formatos posibles son los siguientes:
    * short: dd/mm/aaaa
    * full: dd de mm de aaaa

    :param datetime value: Fecha a ser transformada.
    :param format: Formato con el que mostrar la fecha. Valores posibles: short y full.
    :return: Un string con formato de la fecha.
    """

    value_str = None
    if not value:
        value_str = ''
    if format == 'short':
        value_str = value.strftime('%d/%m/%Y')
    elif format == 'full':
        value_str = value.strftime('%d de %m de %Y')
    else:
        value_str = ''
    return value_str

class WrongDniException(Exception):
    pass

def get_cuil(document_number, gender):
    """Cuil format is: AB - document_number - C-
    Author: Nahuel Sanchez, Woile
    @param {str} document_number -> containing only digits
    @param {str} gender -> 'F' or 'M' or 'S'
    @return {str}
    """
    MALE = ('M', 'MALE', 'HOMBRE')
    FEMALE = ('F', 'FEMALE', 'MUJER')
    SOCIETY = ('S', 'SOCIETY', 'SOCIEDAD')

    if len(document_number) != 8 and document_number.isdigit():
        if len(document_number) == 7:
            document_number = ''.join(['0', document_number])
        else:
            raise WrongDniException(u"document_number incorrect")

    gender = gender.upper()
    if gender in MALE:
        AB = '20'
    elif gender in FEMALE:
        AB = '27'
    else:
        AB = '30'

    #############
    # Los numeros (excepto los dos primeros) que le tengo que
    # multiplicar a la cadena formada por el prefijo y por el
    # numero de documento los tengo almacenados en un arreglo.
    #############
    multipliers = [3, 2, 7, 6, 5, 4, 3, 2]

    # Realizo las dos primeras multiplicaciones por separado.
    calculation = (int(AB[0]) * 5) + (int(AB[1]) * 4)
    for i, digit in enumerate(document_number):
        calculation += (int(digit) * multipliers[i])

    # Mod is calculated here
    rest = calculation % 11

    #############
    # Llevo a cabo la evaluacion de las tres condiciones para
    # determinar el valor de C y conocer el valor definitivo de
    # AB.
    #############

    if gender not in SOCIETY and rest == 1:
        if gender in MALE:
            C = '9'
        else:
            C = '4'
        AB = '23'
    elif rest == 0:
        C = '0'
    else:
        C = 11 - rest
    
    return "{0}{1}{2}".format(AB, document_number, C)
