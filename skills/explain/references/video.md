# Explainer video

Make one only when the user asks. It is slow to build and needs tools many machines lack.

1. **Tools:** probe for ffmpeg, Manim and a text-to-speech engine first, and tell the user what is missing. Without local installs, use the `manimcommunity/manim:stable` Docker image, which includes ffmpeg, on a machine with a few GB of free disk. On a cluster, run it where batch jobs run, and keep the files on storage that machine can see.
2. **Plan:** one question, 60–180 s, in 4–8 scenes. For each scene, write what is on screen at its start and end, and the narration in 80% STE at about 150 words per minute. Show this plan to the user before rendering.
3. **Narration:**
   - With ElevenLabs, ask for the path of a file that holds the key. Never ask for the key in chat.
   - Without a key, use a local voice (for example `piper-tts`), or deliver captions only and say so.
4. **Build:**
   - One audio clip per animation step. Start the animation 0.3–0.5 s before the narration mentions it.
   - Render each scene with `manim -qh`, attach its audio, and join the scenes with ffmpeg's concat demuxer.
5. **Check:**
   - Pull a few frames and look at them with Read.
   - Compare the video and audio durations of each scene.
   - Check every on-screen number against the claim ledger.
6. **Deliver** the .mp4 path, and say what was not done.
