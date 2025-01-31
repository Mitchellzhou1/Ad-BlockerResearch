// Assuming you have included static-filtering-parser.js and can access its functionality
import * as sfp from "./static-filtering-parser.js";
import {
    FilteringContext,
    enableWASM,
    pslInit,
    restart,
} from './main.js';

(async ( ) => {
    await enableWASM('.');

    await fetch('./data/effective_tld_names.dat').then(response => {
        return response.text();
    }).then(pslRaw => {
        pslInit(pslRaw);
    });

    const snfe = await Promise.all([
        fetch('./data/easylist.txt').then(response => {
            return response.text();
        }),
        fetch('./data/easyprivacy.txt').then(response => {
            return response.text();
        }),
    ]).then(rawLists => {
        return restart([
            { name: 'easylist', raw: rawLists[0] },
            { name: 'easyprivacy', raw: rawLists[1] },
        ]);
    });

    // Reuse filtering context: it's what uBO does
    const fctxt = new FilteringContext();

    // Tests
    // Not blocked
    fctxt.setDocOriginFromURL('https://www.bloomberg.com/');
    fctxt.setURL('https://www.bloomberg.com/tophat/assets/v2.6.1/that.css');
    fctxt.setType('stylesheet');
    if ( snfe.matchRequest(fctxt) !== 0 ) {
        console.log(snfe.toLogData());
    }

    // Blocked
    fctxt.setDocOriginFromURL('https://www.bloomberg.com/');
    fctxt.setURL('https://securepubads.g.doubleclick.net/tag/js/gpt.js');
    fctxt.setType('script');
    if ( snfe.matchRequest(fctxt) !== 0 ) {
        console.log(snfe.toLogData());
    }

    // Unblocked
    fctxt.setDocOriginFromURL('https://www.bloomberg.com/');
    fctxt.setURL('https://sourcepointcmp.bloomberg.com/ccpa.js');
    fctxt.setType('script');
    if ( snfe.matchRequest(fctxt) !== 0 ) {
        console.log(snfe.toLogData());
    }

    restart();
})();