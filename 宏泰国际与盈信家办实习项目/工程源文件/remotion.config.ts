import {Config} from '@remotion/cli/config';
Config.setVideoImageFormat('jpeg');
Config.setCodec('h264');
Config.setPixelFormat('yuv420p');
Config.setCrf(18);
Config.setOverwriteOutput(true);
Config.setEntryPoint('./src/index.ts');
// Use an existing local browser when available; do not download another browser.
import {existsSync} from 'node:fs';
const chrome = process.env.BOI_CHROME ?? '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
if (existsSync(chrome)) Config.setBrowserExecutable(chrome);
Config.setConcurrency(4);
