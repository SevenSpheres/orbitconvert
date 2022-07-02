from typing import Optional, Tuple
import warnings
from scipy.spatial.transform import Rotation
import PySimpleGUI as sg

OBLIQUITY = 23.4392911

class ElementsConverter:
    """Converts orbital elements to Celestia convention."""

    def __init__(self, ra: float, dec: float) -> None:
        """Creates a converter for given RA and Dec (both in degrees)."""
        self._convert = Rotation.from_euler('yzx', [-dec-90, ra, -OBLIQUITY], degrees=True)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')  # ignore gimbal lock warning
            self._arg_peri, self._inclination, self._node = self._convert.inv().as_euler('zxz', degrees=True)
        self._inclination = -self._inclination
        self._node += 180
        if self._node >= 360:
            self._node -= 360

    def convert(
        self,
        arg_peri: Optional[float] = None,
        inclination: Optional[float] = None,
        node: Optional[float] = None,
    ) -> Tuple[float, float, float]:
        """Converts orbital elements to Celestia convention. Angles in degrees."""
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')  # ignore gimbal lock warning
            orbit = Rotation.from_euler(
                'zxz',
                [
                    arg_peri if arg_peri is not None else self._arg_peri,
                    inclination if inclination is not None else self._inclination,
                    node if node is not None else self._node,
                ],
                degrees=True,
            )

            arg_peri, inclination, node = (self._convert * orbit).as_euler('zxz', degrees=True)

        if arg_peri < 0:
            arg_peri += 360
        if node < 0:
            node += 360

        return arg_peri, inclination, node

def orbitconvert(ra, dec, inclination, node, arg_peri, exoplanet=False):
    if not inclination and inclination != 0:
        inclination = None
    if not node and node != 0:
        node = None
    if not arg_peri and arg_peri != 0:
        arg_peri = None
    if exoplanet:
        peri += 180 # exoplanets use omega_1 so apply 180 degree correction
    ec = ElementsConverter(ra, dec)
    arg_peri, inclination, node = ec.convert(arg_peri, inclination, node)
    return inclination, node, arg_peri

left = [
    [sg.Text('Plane-of-Sky', font=('arial', 12))],
    [sg.Text('Inclination:', size=(16, 1)), sg.Input(size=(10, 1), key='Inc1')],
    [sg.Text('Ascending Node:', size=(16, 1)), sg.Input(size=(10, 1), key='Node1')],
    [sg.Text('Argument of Periapsis:', size=(16, 1)), sg.Input(size=(10, 1), key='ArgPeri1')],
]
right = [
    [sg.Text('Ecliptic', font=('arial', 12))],
    [sg.Text('Inclination:', size=(16, 1)), sg.Input(size=(10, 1), key='Inc2')],
    [sg.Text('Ascending Node:', size=(16, 1)), sg.Input(size=(10, 1), key='Node2')],
    [sg.Text('Argument of Periapsis:', size=(16, 1)), sg.Input(size=(10, 1), key='ArgPeri2')],
]
layout = [
    [sg.Menu([['File', ['Info', 'Exit']]])],
    [sg.Text('Right Ascension:', size=(16, 1)), sg.Input(size=(10, 1), key='RA'),
    sg.Text(size=(1, 1)), sg.Text('Declination:', size=(16, 1)), sg.Input(size=(10, 1), key='Dec')],
    [sg.Text(size=(50, 1), key='Output'), sg.Button('Convert')],
    [sg.HSeparator()],
    [sg.Column(left), sg.VSeparator(), sg.Column(right)],
]
window = sg.Window('Orbit Frame Converter', layout)

while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED or event == 'Exit':
        break

    if event == 'Info':
        sg.popup('This program is intended to simplify converting orbital parameters from a plane-of-sky reference frame to an ecliptic one, e.g. for use in Celestia.\n\nAuthors: ajtribick & SevenSpheres, 2021-2022', title='Info')

    if event == 'Convert':
        try:
            ra = eval(values['RA'])
            dec = eval(values['Dec'])
            inclination = values['Inc1']
            node = values['Node1']
            arg_peri = values['ArgPeri1']
            if values['Inc1']:
                inclination = eval(inclination)
            if values['Node1']:
                node = eval(node)
            if values['ArgPeri1']:
                arg_peri = eval(arg_peri)
            inclination, node, arg_peri = orbitconvert(ra, dec, inclination, node, arg_peri)
            window['Inc2'].update(inclination)
            window['Node2'].update(node)
            window['ArgPeri2'].update(arg_peri)
            window['Output'].update('')
        except SyntaxError:
            window['Output'].update('Please input RA and Dec!')
        except NameError:
            window['Output'].update('You can only input numbers!')
        except:
            window['Output'].update('Unexpected error encountered.')

window.close()