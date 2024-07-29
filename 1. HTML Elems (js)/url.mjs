export class Url {
    constructor() {
      this.full_address = '';
      this.stripped_address = '';
      this.current_url = '';
    }
  
    cleanUrl(address) {
      let stripped_address = address.replace(/https?:\/\/www\./, '');

      stripped_address = stripped_address.replace(/\//g, '-');
      
      return stripped_address;
    }

    initialize(full_address){
      this.full_address = full_address;
      this.stripped_address = this.cleanUrl(full_address);
      this.current_url = '';
    }
  }
  
