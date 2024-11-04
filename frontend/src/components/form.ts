import { Toast, ToastLevel } from "../components/toast";
import { ShortenedUrlResponse } from "../types";
import copy from "copy-to-clipboard";

export class Form extends HTMLElement {
  private submitBtn: HTMLButtonElement;
  private form: HTMLFormElement;

  constructor() {
    super();

    this.submitBtn = this.querySelector(".btn") as HTMLButtonElement;
    this.form = this.querySelector("form") as HTMLFormElement;
  }

  onBeforeRequest = () => {
    this.form.classList.add("submitting");

    this.submitBtn.classList.add("clicked");
    setTimeout(() => {
      this.submitBtn.classList.remove("clicked");
    }, 200);
  };

  onAfterRequest = () => {
    this.form.classList.remove("submitting");
  };

  onBeforeSwap = (evt: CustomEvent) => {
    const status = evt.detail.xhr.status;
    const toast = document.querySelector("c-toast") as Toast;

    let responseMessage;
    try {
      responseMessage = JSON.parse(evt.detail.serverResponse)["detail"];
    } catch {
      responseMessage = evt.detail.serverResponse;
    }

    if (responseMessage.shortened_url) {
      this.processUrlShortened(responseMessage, toast);
    } else if (status >= 400 && status < 500) {
      toast.show(responseMessage, ToastLevel.WARNING);
    } else if (status >= 500) {
      toast.show("Something went wrong, please try again later.", ToastLevel.ERROR);
    }
  };

  processUrlShortened(responseMessage: ShortenedUrlResponse, toast: Toast) {
    const copied = copy(responseMessage.shortened_url);
    let toastMessage = `Short URL <a class="break-all text-sm font-bold whitespace-pre-wrap" href="${responseMessage.shortened_url}" target="_blank">${responseMessage.shortened_url}</a> created`;
    if (copied) {
      toastMessage += ` and copied to clipboard!`;
      if (responseMessage.expires_at) {
        const expiresAt = new Date(responseMessage.expires_at * 1000).toLocaleString();
        toastMessage += `<br />With expiration date set to ${expiresAt}`;
      }
    } else {
      toastMessage += ` succesfully!`;
    }
    toast.show(toastMessage, ToastLevel.SUCCESS, null);
  }
}

customElements.define("c-form", Form);
