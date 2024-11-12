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
    fctxt.setDocOriginFromURL('https://analytics.justuno.com/');
    fctxt.setURL('https://analytics.justuno.com/');
    // fctxt.setType('stylesheet');
    if ( snfe.matchRequest(fctxt) !== 0 ) {
        console.log(snfe.toLogData()['raw']);
    }

    fctxt.setURL('https://analytics.justuno.com/hi.txt');
    // fctxt.setType('stylesheet');
    if ( snfe.matchRequest(fctxt) !== 0 ) {
        console.log(snfe.toLogData()['raw']);
    }

    fctxt.setURL('https://analytics.justuno.com/robots.txt');
    // fctxt.setType('stylesheet');
    if ( snfe.matchRequest(fctxt) !== 0 ) {
        console.log(snfe.toLogData()['raw']);
    }

    restart();
})();