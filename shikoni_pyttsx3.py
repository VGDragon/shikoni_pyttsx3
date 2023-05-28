import argparse
import pyttsx3

from shikoni.ShikoniClasses import ShikoniClasses
from shikoni.tools.ShikoniInfo import start_shikoni_api
from shikoni.base_messages.ShikoniMessageConnectorSocket import ShikoniMessageConnectorSocket
from shikoni.message_types.ShikoniMessageRun import ShikoniMessageRun


from shikoni.message_types.ShikoniMessageString import ShikoniMessageString



def on_message(msg, shikoni: ShikoniClasses, engine):
    group_name = msg["group_name"]
    messages = msg["messages"]
    tts_text_list = []
    for key, message in messages.items():
        if isinstance(message, ShikoniMessageString):
            tts_text_list.append(message.message)

    tts_text = " ".join(tts_text_list).strip()
    if len(tts_text) < 1:
        shikoni.send_to_all_clients(message=ShikoniMessageRun(), group_name=group_name)
        return

    engine.say(tts_text)
    engine.runAndWait()
    shikoni.send_to_all_clients(message=ShikoniMessageRun(), group_name=group_name)






def start_server(
        server_port: int,
        api_server_port: int,
        server_address: str = "0.0.0.0",
        path: str = ""):
    engine = pyttsx3.init()
    shikoni = ShikoniClasses(default_server_call_function=lambda msg, shikoni: on_message(msg, shikoni, engine))

    # to search for free ports as client
    api_server = start_shikoni_api(api_server_port)

    # start the websocket server
    # if start_loop is false, no messages will be handled
    shikoni.start_base_server_connection(
        connection_data=ShikoniMessageConnectorSocket().set_variables(url=server_address,
                                                                      port=server_port,
                                                                      is_server=True,
                                                                      connection_name="001",
                                                                      connection_path=path),
        start_loop=True)
    # close
    api_server.terminate()
    shikoni.close_base_server()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Skikoni Server")
    parser.add_argument("-p", "--port", dest="port", type=int, help="server port ()")
    parser.add_argument("--api", dest="api_port", type=int, help="api server port (PORT + 1)")
    parser.add_argument("--path", dest="path", type=str,
                        help="the path to use for the base server. can be used for security")

    args = parser.parse_args()
    server_port = 19998
    path = ""
    if args.port:
        server_port = args.port
    api_server_port = server_port + 1
    if args.api_port:
        api_server_port = args.api_port
    if args.path:
        path = args.path

    start_server(server_port=server_port, api_server_port=api_server_port, path=path)
