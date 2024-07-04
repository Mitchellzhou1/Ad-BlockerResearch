export class Result {
  constructor() {
    this.elem_indx = 0;
    this.page_source = '';
    this.initial_outer_html = '';
    this.after_outer_html = '';
    this.initial_local_DOM = '';
    this.after_local_DOM = '';
    this.initial_manual = '';
    this.after_manual = '';
    this.initial_tag = 0;
    this.after_tag = 0;
    this.DOM_changed = false;
    this.outer_HTML_changed = false;
    this.manual_change = false;
  }
}