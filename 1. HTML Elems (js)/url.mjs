export class Url {
    constructor() {
      this.full_address = '';
      this.stripped_address = '';
      this.current_url = '';
      this.key = '';
    }
  
initialize(full_address){
      this.full_address = full_address;
      this.stripped_address = this.cleanUrl(full_address);
      this.key = this.website_key(full_address);
      this.current_url = '';
    }

    cleanUrl(address) {
      let stripped_address = address.replace(/https?:\/\/www\./, '');

      stripped_address = stripped_address.replace(/\//g, '-');
      
      return stripped_address;
    }

    website_key(full_address){
      try {
        var website_root = full_address.split("://")[1];
        
        if (website_root.includes('www')) {
            website_root = website_root.split('.').slice(1).join('_');
        } else {
            website_root = website_root.split('.').join('_');
        }
    
        website_root = website_root.replace(/\//g, '-');
      } catch (error) {
          console.log((full_address + "\n").repeat(100));
          console.error(error);
          website_root = full_address.replace(/\//g, '-');
      }
      return website_root;
    };


  }
  
