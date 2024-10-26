# AI devs 3
My private attempts to solve AI devs 3 training tasks.
All private API keys and passwords are stored in secrets.py file (in the format shown in public example-secrets.py file).
For now it includes the following:
- lib/aidevs.py - simple library to interface with the AI devs official system (for sending answers - and whatever else shows up in the future)
- lib/usedtokens.py - simple library to track tokens usage inside a script (to understand if we're getting any significant costs)
- prework.py - simple solution to the "prework" task (get 2 strings from a remote file and submit them as list)

The following are Python re-writes of 3rd-devs examples (https://github.com/i-am-alice/3rd-devs)
- 3rd-devs-completion.py
- 3rd-devs-chain.py
