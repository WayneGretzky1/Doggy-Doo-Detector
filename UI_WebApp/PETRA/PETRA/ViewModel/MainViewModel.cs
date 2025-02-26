using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System.Collections.ObjectModel;
using System.ComponentModel;

namespace PETRA.ViewModel

{
    public partial class MainViewModel : ObservableObject
    {

        public MainViewModel()
        {
            items = new ObservableCollection<string>();
        }

        [ObservableProperty]
        ObservableCollection<string> items;

        [ObservableProperty]
        string text;

        [RelayCommand]
        void Add()
        {
            if (string.IsNullOrWhiteSpace(Text))
                return;

            Items.Add(text);
            // add our item
            Text = string.Empty;
        }
    }


}
