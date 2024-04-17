typeof browser<"u"&&(chrome=browser),(()=>{"use strict";var h={};function m(t,a="440px"){const e=document.createElement("ghostery-iframe-wrapper"),i=e.attachShadow({mode:"closed"}),s=document.createElement("template");s.innerHTML=`
    <iframe src="${t}" frameborder="0"></iframe>
    <style>
      :host {
        all: initial;
        display: flex !important;
        align-items: flex-end;
        position: fixed;
        top: 10px;
        right: 10px;
        left: 10px;
        bottom: 10px;
        z-index: 2147483647;
        pointer-events: none;
      }

      iframe {
        display: block;
        flex-grow: 1;
        width: min(100%, ${a});
        pointer-events: auto;
        box-shadow: 30px 60px 160px rgba(0, 0, 0, 0.4);
        border-radius: 16px;
        background: linear-gradient(90deg, rgba(0, 0, 0, 0.13) 0%, rgba(0, 0, 0, 0.27) 100%);
        opacity: 0;
        transition: opacity 0.2s ease-in-out, transform 0.2s ease-in-out;
        transform: translateY(20px);
      }

      iframe.active {
        opacity: 1;
        transform: translateY(0);
      }

      @media screen and (min-width: 640px) {
        :host {
          justify-content: flex-end;
          align-items: start;
        }

        iframe {
          flex-grow: 0;
          transform: translateY(-20px);
          max-width: ${a};
        }
      }
    </style>
  `,i.appendChild(s.content),document.documentElement.appendChild(e);const r=i.querySelector("iframe");setTimeout(()=>{r.classList.add("active")},100),window.addEventListener("message",o=>{var d;switch((d=o.data)==null?void 0:d.type){case"ghostery-resize-iframe":{const{height:p,width:l}=o.data;r.style.height=p+"px",l&&(r.style.width=l+"px");break}case"ghostery-close-iframe":o.data.clear&&chrome.runtime.sendMessage({action:"clearIframe",url:t}),o.data.reload?window.location.reload():setTimeout(()=>e.parentElement.removeChild(e),0);break;case"ghostery-clear-iframe":r.src===o.data.url&&setTimeout(()=>e.parentElement.removeChild(e),0);break;default:break}})}function c(t=!1,a=!1){setTimeout(()=>{window.parent.postMessage({type:"ghostery-close-iframe",reload:t,clear:a},"*")},100)}function u(t){new ResizeObserver(()=>{window.parent.postMessage({type:"ghostery-resize-iframe",height:document.body.clientHeight,width:t},"*")}).observe(document.body,{box:"border-box"}),document.body.style.overflow="hidden",chrome.runtime.onMessage.addListener(e=>{e.action==="clearIframe"&&(console.log("clearIframe",e.url),window.parent.postMessage({type:"ghostery-clear-iframe",url:e.url},"*"))})}const f=["ytd-watch-flexy:not([hidden]) ytd-enforcement-message-view-model > div.ytd-enforcement-message-view-model"];let n=!1;chrome.storage.local.get(["youtube_dont_show_again"],t=>{t.youtube_dont_show_again||chrome.extension.inIncognitoContext||(window.addEventListener("yt-navigate-start",()=>{n=!1,c()},!0),setInterval(()=>{!n&&document.querySelectorAll(f).length>0&&(m(chrome.runtime.getURL(`app/templates/youtube.html?url=${encodeURIComponent(window.location.href)}`),"460px"),n=!0)},2e3))})})();
