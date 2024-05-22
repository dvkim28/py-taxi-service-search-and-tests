from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Driver, Car, Manufacturer
from .forms import (DriverCreationForm,
                    DriverLicenseUpdateForm,
                    CarForm, DriverSearchForm,
                    ManufacturerSearchForm,
                    CarSearchForm)


@login_required
def index(request):
    """View function for the home page of the site."""

    num_drivers = Driver.objects.count()
    num_cars = Car.objects.count()
    num_manufacturers = Manufacturer.objects.count()

    num_visits = request.session.get("num_visits", 0)
    request.session["num_visits"] = num_visits + 1

    context = {
        "num_drivers": num_drivers,
        "num_cars": num_cars,
        "num_manufacturers": num_manufacturers,
        "num_visits": num_visits + 1,
    }

    return render(request, "taxi/index.html", context=context)


class ManufacturerListView(LoginRequiredMixin, generic.ListView):
    model = Manufacturer
    context_object_name = "manufacturer_list"
    template_name = "taxi/manufacturer_list.html"
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super(ManufacturerListView, self).get_context_data(**kwargs)
        context["ManufacturerSearchForm"] = ManufacturerSearchForm()
        return context

    def get_queryset(self):
        manufacturer_form = ManufacturerSearchForm(self.request.GET)
        if manufacturer_form.is_valid():
            return Manufacturer.objects.filter(
                name__icontains=manufacturer_form.cleaned_data["name"]
            )
        return Manufacturer.objects.all()


class ManufacturerCreateView(LoginRequiredMixin, generic.CreateView):
    model = Manufacturer
    fields = "__all__"
    success_url = reverse_lazy("taxi:manufacturer-list")


class ManufacturerUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Manufacturer
    fields = "__all__"
    success_url = reverse_lazy("taxi:manufacturer-list")


class ManufacturerDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Manufacturer
    success_url = reverse_lazy("taxi:manufacturer-list")


class CarListView(LoginRequiredMixin, generic.ListView):
    model = Car
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super(CarListView, self).get_context_data(**kwargs)
        context["CarSearchForm"] = CarSearchForm()
        return context

    def get_queryset(self):
        queryset = Car.objects.select_related("manufacturer")
        car_form = CarSearchForm(self.request.GET)
        if car_form.is_valid():
            return queryset.filter(
                model__icontains=car_form.cleaned_data["model"]
            )
        return queryset


class CarDetailView(LoginRequiredMixin, generic.DetailView):
    model = Car


class CarCreateView(LoginRequiredMixin, generic.CreateView):
    model = Car
    form_class = CarForm
    success_url = reverse_lazy("taxi:car-list")


class CarUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Car
    form_class = CarForm
    success_url = reverse_lazy("taxi:car-list")


class CarDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Car
    success_url = reverse_lazy("taxi:car-list")


class DriverListView(LoginRequiredMixin, generic.ListView):
    model = Driver
    template_name = "taxi/driver_list.html"

    def get_context_data(self, **kwargs):
        context = super(DriverListView, self).get_context_data(**kwargs)
        context["DriverForm"] = DriverSearchForm()
        return context

    def get_queryset(self):
        form = DriverSearchForm(self.request.GET)
        if form.is_valid():
            return Driver.objects.filter(
                username__icontains=form.cleaned_data["username"])
        return Driver.objects.all()


class DriverDetailView(LoginRequiredMixin, generic.DetailView):
    model = Driver
    queryset = Driver.objects.all().prefetch_related("cars__manufacturer")


class DriverCreateView(LoginRequiredMixin, generic.CreateView):
    model = Driver
    form_class = DriverCreationForm


class DriverLicenseUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Driver
    form_class = DriverLicenseUpdateForm
    success_url = reverse_lazy("taxi:driver-list")


class DriverDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Driver
    success_url = reverse_lazy("")


@login_required
def toggle_assign_to_car(request, pk):
    driver = Driver.objects.get(id=request.user.id)
    if (
        Car.objects.get(id=pk) in driver.cars.all()
    ):  # probably could check if car exists
        driver.cars.remove(pk)
    else:
        driver.cars.add(pk)
    return HttpResponseRedirect(reverse_lazy("taxi:car-detail", args=[pk]))
