import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import Button from "../Button";

describe("Button", () => {
  it("renders children", () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText("Click me")).toBeInTheDocument();
  });

  it("shows spinner when loading", () => {
    render(<Button loading>Submit</Button>);
    // Button should be disabled
    expect(screen.getByRole("button")).toBeDisabled();
    // Loading svg present
    expect(screen.getByRole("button").querySelector("svg")).toBeTruthy();
  });

  it("is disabled when disabled prop set", () => {
    render(<Button disabled>Disabled</Button>);
    expect(screen.getByRole("button")).toBeDisabled();
  });

  it("calls onClick when clicked", () => {
    const fn = jest.fn();
    render(<Button onClick={fn}>Go</Button>);
    fireEvent.click(screen.getByRole("button"));
    expect(fn).toHaveBeenCalledTimes(1);
  });

  it("does not call onClick when disabled", () => {
    const fn = jest.fn();
    render(<Button disabled onClick={fn}>Go</Button>);
    fireEvent.click(screen.getByRole("button"));
    expect(fn).not.toHaveBeenCalled();
  });

  it("applies danger variant class", () => {
    render(<Button variant="danger">Delete</Button>);
    expect(screen.getByRole("button").className).toContain("bg-red-600");
  });
});
