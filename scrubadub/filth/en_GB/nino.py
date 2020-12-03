from faker import Faker

from scrubadub.filth.base import Filth


class NinoFilth(Filth):
    type = 'nino'

    @staticmethod
    def generate(faker: Faker) -> str:
        """Generates an example of this ``Filth`` type, usually using the faker python library.

        :param faker: The ``Faker`` class from the ``faker`` library
        :type faker: Faker
        :return: An example of this ``Filth``
        :rtype: str
        """
        return faker.ssn()
