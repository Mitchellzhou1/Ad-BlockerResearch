import { readFile } from 'fs/promises';
import {
    FilteringContext,
    // enableWASM,
    // pslInit,
    restart,
} from './main.js';

(async ( ) => {
    // await enableWASM('.');

    // await fetch('./data/effective_tld_names.dat').then(response => {
    //     return response.text();
    // }).then(pslRaw => {
    //     pslInit(pslRaw);
    // });

    const snfe = await Promise.all([
        readFile('./blacklists/easylist.txt', 'utf-8'),
        readFile('./blacklists/easyprivacy.txt', 'utf-8'),
        readFile('./blacklists/peterlowe.txt', 'utf-8'),
    ]).then(rawLists => {
        return restart([
            { name: 'easylist', raw: rawLists[0] },
            { name: 'easyprivacy', raw: rawLists[1] },
            { name: 'peterlowe', raw: rawLists[2] },
        ]);
    });

    console.log("finished reading blacklists");

    // Reuse filtering context: it's what uBO does
    const fctxt = new FilteringContext();

    // Tests
    fctxt.setDocOriginFromURL('https://www.uxmatters.com/');                                                // this is the website URL
    fctxt.setURL('https://www.uxmatters.com/images/sponsors/UXmattersPatreonBanner.png');                 // this is the resource URL
    // fctxt.setType('stylesheet'); 
    if ( snfe.matchRequest(fctxt) !== 0 ) {
        console.log(snfe.toLogData());
    }

    restart();
})();