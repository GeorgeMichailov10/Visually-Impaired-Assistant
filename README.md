## Inspiration

The inspiration for this project came from the desire to empower visually impaired individuals by providing them with a tool to help them enhance their ability to interact with their environment. Both Brij and George have been struggling with slowly losing our vision and needing stronger and stronger glasses to see, which has been challenging, so the challenge on the visually impaired must exponentially more difficult. This way, we can make it a little bit easier.

## What it does

This assistant listens to the user, waiting to hear the activation phrase ('hey echo') similar to how 'hey Siri' works on iPhone. This input is turned from speech to text by a lightweight model (Vosk). When the activation phrase is triggered, the assistant listens to what the user wants to do and classifies it as text recognition such as reading off a screen or book page, describing the key objects from the user's point of view, locating objects, guiding a user to an object or location, and ignoring inappropriate or unaccounted for requests. For each of these requests, it adds a system prompt and iterates until the goal is complete.

## How we built it

We built this by first building out the utilities (handling input, output audio, handling screen, LLM interface, etc.). Then we built out the functions for each goal. Finally we test ran through each function dozens of times and adjusted the prompt and process whenever we saw an issue.

## Challenges we ran into

Originally, we wanted to run the new Qwen2.5-VL-3B model rather than using an online API. We built out the entire interface and multithreaded queue handling and at first it seemed great: all of the text queries were getting fast and accurate responses. Unfortunately, due to the transformers-based architecture, VRAM memory needs scale exponentially, not linearly, so when we started trying to analyze a single image, it required approximately 30GB of VRAM total which is what something only an enterprise level GPU can handle (A100 or H100 bare minimum). This was frustrating since the entire design that had been built out over the previous 3 hours was now obsolete. Other challenges we ran into included the streaming aspect. Since this assistant relies on visual and audio input, we wanted to get the user POV onto the screen using our phones through a Whatsapp call. Unfortunately, the audio being input couldn't be read correctly, so we had to problem solve and try with OBS Studio until finally settling on using a webcam directly through the camera app.

## Accomplishments that we're proud of

The most difficult part of this project (that we ironically weren't even able to put in the final project) was the multithreaded design to handle tasks.

## What we learned

We learned how to think from the perspective of a user rather than the perspective of a creator. We didn't realize just how much giving constant instructions was until we tried to do this with out eyes closed and ran into everything. It was a really eye-opening experience and it made our assistant much better once we realized that and addressed it.

## Future Improvements

We would run this on a VM with two A100 GPUs where we can run them sequentially or even against each other in order to correct each other's answers. We would also be able to implement chain of thought models for the guidance on room navigation once models like o1 and DeepSeek R1 to come up with the best plans.
