import { Toast, ToastLevel } from "../components/toast";
import { ShortenedUrlResponse } from "../types";
import copy from "copy-to-clipboard";

export class Form extends HTMLElement {
  private submitBtn: HTMLButtonElement;
  private form: HTMLFormElement;
  private shortPathInput: HTMLInputElement;
  private fullUrlInput: HTMLInputElement;

  public toast: Toast;

  constructor() {
    super();

    this.submitBtn = this.querySelector(".btn") as HTMLButtonElement;
    this.form = this.querySelector("form") as HTMLFormElement;
    this.shortPathInput = this.querySelector("input[name='short_path']") as HTMLInputElement;
    this.fullUrlInput = this.querySelector("input[name='full_url']") as HTMLInputElement;

    this.toast = document.querySelector("c-toast") as Toast;
  }

  onBeforeRequest = () => {
    this.form.classList.add("submitting");

    this.submitBtn.classList.add("clicked");
    setTimeout(() => {
      this.submitBtn.classList.remove("clicked");
    }, 200);
    window.umami.track("url_shorten_requested", {
      shortPath: this.shortPathInput.value.trim(),
      fullUrl: this.fullUrlInput.value.trim(),
    });
  };

  onAfterRequest = () => {
    this.form.classList.remove("submitting");
  };

  onBeforeSwap = (evt: CustomEvent) => {
    const status = evt.detail.xhr.status;

    let responseMessage;
    try {
      responseMessage = JSON.parse(evt.detail.serverResponse)["detail"];
    } catch {
      responseMessage = evt.detail.serverResponse;
    }

    if (responseMessage.shortened_url) {
      this.processUrlShortened(responseMessage, status);
    } else if (status >= 400 && status < 500) {
      this.toast.show(responseMessage, ToastLevel.WARNING);
    } else if (status >= 500) {
      this.toast.show("Something went wrong, please try again later.", ToastLevel.ERROR);
    }
  };

  constructToastMessage(
    responseMessage: ShortenedUrlResponse,
    isCreated: boolean,
    shouldPromote: boolean,
  ) {
    const isCopied = copy(responseMessage.shortened_url);
    let toastMessage = `
      <a class="break-all text-sm font-bold whitespace-pre-wrap" href="${responseMessage.shortened_url}" target="_blank" rel="nofollow">${responseMessage.shortened_url}</a> short link
    `;
    if (isCopied) {
      if (isCreated) {
        toastMessage += ` is created and copied to clipboard!`;
      } else {
        toastMessage += ` is copied to clipboard!`;
      }
    } else {
      if (isCreated) {
        toastMessage += ` is created!`;
      } else {
        toastMessage += ` is already created!`;
      }
    }
    if (responseMessage.expires_at) {
      const expiresAt = new Date(responseMessage.expires_at * 1000).toLocaleString();
      toastMessage += `<br/> Expires at ${expiresAt}`;
    }
    if (shouldPromote) {
      toastMessage += `
        </br> <a href="/donation/checkout?client_reference_id=${responseMessage.short_path}" class="cursor-pointer font-bold underline">⭐ Make it permanent</a>
      `;
    }
    return toastMessage;
  }

  processUrlShortened(responseMessage: ShortenedUrlResponse, status: number) {
    const isCreated = status === 201;
    const shouldPromote =
      isCreated && this.shortPathInput.value.trim() === responseMessage.short_path;
    const toastMessage = this.constructToastMessage(responseMessage, isCreated, shouldPromote);
    this.toast.show(toastMessage, ToastLevel.SUCCESS, null);
    window.umami.track("url_shortened", {
      shortPath: responseMessage.short_path,
      isCreated,
      shouldPromote,
    });
  }
}

customElements.define("c-form", Form);
