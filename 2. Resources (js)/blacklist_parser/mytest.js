import { readFile } from 'fs/promises';
import {
    FilteringContext,
    // enableWASM,
    // pslInit,
    restart,
} from './main.js';

// Import yargs using ES modules
import yargs from 'yargs';
import { hideBin } from 'yargs/helpers';

(async ( ) => {
    // await enableWASM('.');

    // await fetch('./data/effective_tld_names.dat').then(response => {
    //     return response.text();
    // }).then(pslRaw => {
    //     pslInit(pslRaw);
    // });

    const argv = yargs(hideBin(process.argv))
        .option('url', {
            alias: 'u',
            type: 'string',
            description: 'The website URL',
        })
        .option('resource', {
            alias: 'r',
            type: 'string',
            description: 'The resource',
        })
        .parse();

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

    // console.log("finished reading blacklists");

    // Reuse filtering context: it's what uBO does
    const fctxt = new FilteringContext();

    // Tests
    // fctxt.setDocOriginFromURL('https://analytics.justuno.com/');
    fctxt.setDocOriginFromURL(`${argv.url}`);
    // fctxt.setURL('https://analytics.justuno.com/');
    fctxt.setURL(`${argv.resource}`);
    // fctxt.setType('stylesheet');
    if ( snfe.matchRequest(fctxt) !== 0 ) {
        console.log(snfe.toLogData()['raw']);
    }

    restart();
})();