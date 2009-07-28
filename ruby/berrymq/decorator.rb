require 'weakref'

module BerryMQ
  #
  #This module supports method decoration.
  #Internal use only
  #
  module DecoratorManager
    @@__decorators = Hash.new {|hash, key| hash[key] = []}
    def self.new_decorator(klass, key, id_obj, args)
      @@__decorators[klass].push(Decorator.new(key, id_obj, args))
    end
    def self.method_added(klass, method_name)
      last_obj = @@__decorators[klass].last
      if last_obj != nil
        last_obj.method_name = method_name
        @@__decorators[klass].push(nil)
      end
    end
    def self.get_decorators(klass)
      @@__decorators[klass]
    end
    def self.decorate_object(target_obj)
      auto_twitter = nil
      self.get_decorators(target_obj.class).each {|decorator|
        next if decorator == nil
        auto_twitter = decorator if decorator.key == :auto_twitter
      }
      self.override_method(target_obj, auto_twitter) if auto_twitter != nil
      self.get_decorators(target_obj.class).each {|decorator|
        next if decorator == nil
        if decorator.key == :following
          BerryMQ::RootTransporter::regist_follower(target_obj, decorator)
        end
      }      
    end

    def self.override_method(target_obj, decorator)
      if decorator != nil
        id_ojb = decorator.id
        method_name = decorator.method_name
        method_obj = target_obj.method(method_name)
        entry, exit = auto_twitter.args
        if entry && exit
          entry_id = BerryMQ::Identifier.new(id_obj, "entry")
          exit_id = BerryMQ::Identifier.new(id_obj, "exit")
          target_obj.__send__(:define_method, method_name) { |args|
            BerryMQ::twitter(entry_id, args)
            result = method_obj.call(*args)
            BerryMQ::twitter(exit_id, result)
            result
          }
        elsif entry == true
          entry_id = BerryMQ::Identifier.new(id_obj, "entry")
          target_obj.__send__(:define_method, method_name) { |args|
            BerryMQ::twitter(entry_id, args)
            method_obj.call(*args)
          }
        elsif exit == true
          exit_id = BerryMQ::Identifier.new(id_obj, "exit")
          target_obj.__send__(:define_method, method_name) { |args|
            result = method_obj.call(*args)
            BerryMQ::twitter(exit_id, result)
            result
          }
        end
      end
    end
  end
  class Decorator
    attr_reader :key, :args, :method_name, :id
    attr_writer :method_name
    def initialize(key, id_obj, args)
      @key = key
      @id = id_obj
      @args = args
      @method_name = nil
    end
  end
  class WeakRefMethod
    attr_reader :method_name
    def initialize(target_obj, method_name)
      @target_obj = WeakRef.new(target_obj)
      @method_name = method_name
    end
    def call(args)
      @target_obj.__send__(@method_name, *args)
    end
    def alive?
      @target_obj.weakref_alive?
    end
  end
end
