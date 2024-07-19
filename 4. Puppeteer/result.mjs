export class Result {
  constructor() {
    this.initial_outer_html = '';
    this.after_outer_html = '';
    this.initial_local_DOM = '';
    this.after_local_DOM = '';
    this.initial_manual = '';
    this.after_manual = '';
    this.initial_tags = 0;
    this.after_tags = 0;
    this.local_DOM_changed = false;
    this.outer_HTML_changed = false;
    this.manual_change = false;
  }
  reset(){
    this.initial_outer_html = '';
    this.after_outer_html = '';
    this.initial_local_DOM = '';
    this.after_local_DOM = '';
    this.initial_manual = '';
    this.after_manual = '';
    this.initial_tags = 0;
    this.after_tags = 0;
    this.local_DOM_changed = false;
    this.outer_HTML_changed = false;
    this.manual_change = false;
  }
}