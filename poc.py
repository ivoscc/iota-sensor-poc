# -*- coding: utf-8 -*-
"""
Read sensor data from the Public NetAtmo API, tag it with a price and attach it
as transaction to the Tangle.
"""
import json
from six import text_type

from iota import Iota
from netatmo import APIClient, get_sensor_options
from sender import get_iota_options, attach_tagged_data
from cli import configure_argument_parser
from buffer import Buffer


def main(iota_options, sensor_options, file_buffer):
    # configure NetAtmo API client
    sensor_api = APIClient(sensor_options.client_id,
                           sensor_options.client_secret,
                           sensor_options.username,
                           sensor_options.password)
    # configure IOTA API client
    iota_api = Iota(iota_options.node,
                    iota_options.seed.encode('ascii'))
    # get NetAtmo data
    netatmo_query = {
        'lat_ne': 3,
        'lon_ne': 4,
        'lat_sw': -2,
        'lon_sw': -2,
        'filter': True,
        'required_data': 'temperature'
    }

    sensor_data = sensor_api.get_public_data(netatmo_query)
    file_buffer.add(json.dumps(sensor_data).encode('ascii'))
    if not file_buffer.is_ready:
        return
    sensor_data = file_buffer.read()
    # tag the transaction with the configured price
    transaction_data = { 'price': iota_options.price, 'data': sensor_data }
    # encode data and attach it to the IOTA tangle
    attach_tagged_data(iota_api,
                       iota_options.address,
                       json.dumps(transaction_data).encode('ascii'),
                       iota_options.tag)
    file_buffer.clear()

if __name__ == '__main__':
    parser = configure_argument_parser(__doc__, ['iota', 'sensor'])

    parser.add_argument(
        '--buffer-size',
        default=0,
        help=('how many NetAtmo responses to store locally before attaching '
              'them to the Tangle (defaults to 0)'),
        type=int
    )
    parser.add_argument(
        '--buffer-directory',
        type=text_type,
        help=(('directory to store NetAtmo responses before attaching them as'
               ' a single chunk.')),
    )

    cli_args = parser.parse_args()
    file_buffer = Buffer.from_arguments(cli_args)
    sensor_options = get_sensor_options(cli_args)
    iota_options = get_iota_options(cli_args)
    main(iota_options, sensor_options, file_buffer)
