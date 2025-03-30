// blacklistInitializer.js
import { readFile } from 'fs/promises';
import { FilteringContext, restart } from './main.js';

let snfe;

export const initializeBlacklists = async () => {
    if (!snfe) {
        const rawLists = await Promise.all([
            readFile('./blacklist_parser/blacklists/easylist.txt', 'utf-8'),
            readFile('./blacklist_parser/blacklists/easyprivacy.txt', 'utf-8'),
            readFile('./blacklist_parser/blacklists/peterlowe.txt', 'utf-8'),
        ]);

        snfe = await restart([
            { name: 'easylist', raw: rawLists[0] },
            { name: 'easyprivacy', raw: rawLists[1] },
            { name: 'peterlowe', raw: rawLists[2] },
        ]);

    }
    return snfe;
};

// Export FilteringContext to allow its use elsewhere
export { FilteringContext };
